#!/bin/bash
# Full-Stack AI Chat — AWS Infrastructure Setup
# Run each section step by step. Replace placeholders with your values.

set -e

# ============================================================
# CONFIGURATION — Update these values
# ============================================================
AWS_REGION="ap-south-1"
AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
PROJECT_NAME="fullstack-ai-chat"
DOMAIN="yourdomain.com"
VPC_CIDR="10.0.0.0/16"

echo "=== Full-Stack AI Chat AWS Setup ==="
echo "Region: $AWS_REGION"
echo "Account: $AWS_ACCOUNT_ID"
echo ""

# ============================================================
# 1. ECR Repositories
# ============================================================
echo "--- Creating ECR Repositories ---"

aws ecr create-repository \
  --repository-name ${PROJECT_NAME}-backend \
  --region $AWS_REGION \
  --image-scanning-configuration scanOnPush=true

aws ecr create-repository \
  --repository-name ${PROJECT_NAME}-frontend \
  --region $AWS_REGION \
  --image-scanning-configuration scanOnPush=true

echo "ECR repos created."

# ============================================================
# 2. VPC + Subnets
# ============================================================
echo "--- Creating VPC ---"

VPC_ID=$(aws ec2 create-vpc \
  --cidr-block $VPC_CIDR \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${PROJECT_NAME}-vpc}]" \
  --query 'Vpc.VpcId' --output text)

echo "VPC created: $VPC_ID"

# Enable DNS
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

# Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${PROJECT_NAME}-igw}]" \
  --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# Public Subnets (for ALB)
PUB_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ${AWS_REGION}a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-public-1}]" \
  --query 'Subnet.SubnetId' --output text)

PUB_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ${AWS_REGION}b \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-public-2}]" \
  --query 'Subnet.SubnetId' --output text)

# Private Subnets (for ECS + ElastiCache)
PRIV_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.10.0/24 --availability-zone ${AWS_REGION}a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-private-1}]" \
  --query 'Subnet.SubnetId' --output text)

PRIV_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.11.0/24 --availability-zone ${AWS_REGION}b \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-private-2}]" \
  --query 'Subnet.SubnetId' --output text)

echo "Subnets created."

# ============================================================
# 3. Security Groups
# ============================================================
echo "--- Creating Security Groups ---"

# ALB Security Group (allows 80, 443 from internet)
ALB_SG=$(aws ec2 create-security-group \
  --group-name ${PROJECT_NAME}-alb-sg \
  --description "ALB Security Group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 443 --cidr 0.0.0.0/0

# ECS Security Group (allows traffic from ALB only)
ECS_SG=$(aws ec2 create-security-group \
  --group-name ${PROJECT_NAME}-ecs-sg \
  --description "ECS Tasks Security Group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress --group-id $ECS_SG --protocol tcp --port 3000 --source-group $ALB_SG
aws ec2 authorize-security-group-ingress --group-id $ECS_SG --protocol tcp --port 8000 --source-group $ALB_SG

# Redis Security Group (allows traffic from ECS only)
REDIS_SG=$(aws ec2 create-security-group \
  --group-name ${PROJECT_NAME}-redis-sg \
  --description "ElastiCache Security Group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress --group-id $REDIS_SG --protocol tcp --port 6379 --source-group $ECS_SG

echo "Security groups created."

# ============================================================
# 4. ElastiCache (Redis)
# ============================================================
echo "--- Creating ElastiCache Redis ---"

aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name ${PROJECT_NAME}-redis-subnet \
  --cache-subnet-group-description "Redis subnet group" \
  --subnet-ids $PRIV_SUBNET_1 $PRIV_SUBNET_2

aws elasticache create-cache-cluster \
  --cache-cluster-id ${PROJECT_NAME}-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --cache-subnet-group-name ${PROJECT_NAME}-redis-subnet \
  --security-group-ids $REDIS_SG

echo "ElastiCache cluster creating (takes ~5 min)..."

# ============================================================
# 5. ECS Cluster
# ============================================================
echo "--- Creating ECS Cluster ---"

aws ecs create-cluster \
  --cluster-name ${PROJECT_NAME} \
  --capacity-providers FARGATE \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1

echo "ECS cluster created."

# ============================================================
# 6. CloudWatch Log Groups
# ============================================================
echo "--- Creating CloudWatch Log Groups ---"

aws logs create-log-group --log-group-name /ecs/${PROJECT_NAME}-backend
aws logs create-log-group --log-group-name /ecs/${PROJECT_NAME}-frontend
aws logs put-retention-policy --log-group-name /ecs/${PROJECT_NAME}-backend --retention-in-days 30
aws logs put-retention-policy --log-group-name /ecs/${PROJECT_NAME}-frontend --retention-in-days 30

echo "Log groups created."

# ============================================================
# 7. Store OpenAI API Key in SSM
# ============================================================
echo "--- Store your OpenAI API key ---"
echo "Run manually:"
echo "  aws ssm put-parameter --name '/${PROJECT_NAME}/openai-api-key' --value 'sk-YOUR-KEY' --type SecureString"

# ============================================================
# Done
# ============================================================
echo ""
echo "=== Infrastructure Created ==="
echo "VPC: $VPC_ID"
echo "Public Subnets: $PUB_SUBNET_1, $PUB_SUBNET_2"
echo "Private Subnets: $PRIV_SUBNET_1, $PRIV_SUBNET_2"
echo "ALB SG: $ALB_SG"
echo "ECS SG: $ECS_SG"
echo "Redis SG: $REDIS_SG"
echo ""
echo "Next steps:"
echo "1. Wait for ElastiCache to be available"
echo "2. Create ALB with target groups"
echo "3. Register ECS task definition (task-definition.json)"
echo "4. Create ECS service"
echo "5. Set up GitHub Actions secrets"
echo "6. Push code to trigger deploy"
