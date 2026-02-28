import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        chat: {
          bg: "#0f0f0f",
          sidebar: "#171717",
          input: "#1e1e1e",
          hover: "#2a2a2a",
          border: "#333333",
          user: "#2563eb",
          assistant: "#1e1e1e",
        },
      },
    },
  },
  plugins: [],
};
export default config;
