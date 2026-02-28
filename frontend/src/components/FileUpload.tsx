"use client";

import { useCallback, useRef } from "react";
import { formatFileSize, getFileIcon } from "@/lib/utils";
import { Paperclip, X } from "lucide-react";

const ALLOWED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "image/png",
  "image/jpeg",
  "image/webp",
];

const MAX_SIZE = 10 * 1024 * 1024; // 10MB

interface FileUploadProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
}

export default function FileUpload({ files, onFilesChange }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (newFiles: FileList | null) => {
      if (!newFiles) return;
      const valid = Array.from(newFiles).filter((f) => {
        if (!ALLOWED_TYPES.includes(f.type)) {
          alert(`Unsupported file type: ${f.name}`);
          return false;
        }
        if (f.size > MAX_SIZE) {
          alert(`File too large (max 10MB): ${f.name}`);
          return false;
        }
        return true;
      });
      onFilesChange([...files, ...valid]);
    },
    [files, onFilesChange],
  );

  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles],
  );

  const fileTypeFromName = (name: string): string => {
    const ext = name.split(".").pop()?.toLowerCase();
    if (ext === "pdf") return "pdf";
    if (ext === "docx") return "docx";
    if (ext === "xlsx") return "xlsx";
    return "image";
  };

  return (
    <div>
      {/* File chips */}
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {files.map((file, i) => (
            <div
              key={i}
              className="flex items-center gap-1.5 px-2 py-1 bg-chat-hover rounded-md border border-chat-border text-xs text-gray-300"
            >
              <span>{getFileIcon(fileTypeFromName(file.name))}</span>
              <span className="truncate max-w-[120px]">{file.name}</span>
              <span className="text-gray-500">{formatFileSize(file.size)}</span>
              <button
                onClick={() => removeFile(i)}
                className="text-gray-500 hover:text-red-400"
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Hidden input */}
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg,.webp"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      {/* Attach button */}
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="p-2 text-gray-400 hover:text-gray-200 transition-colors"
        title="Attach files (PDF, DOCX, XLSX, Images)"
      >
        <Paperclip size={18} />
      </button>
    </div>
  );
}
