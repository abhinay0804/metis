import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, File, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile?: File | null;
  onFileRemove?: () => void;
}

const FileUpload = ({ onFileSelect, selectedFile, onFileRemove }: FileUploadProps) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'text/plain': ['.txt'],
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const ACCEPT_EXTS = '.pdf,.png,.jpg,.jpeg,.pptx,.xlsx,.xls,.docx,.csv,.json,.txt';

  if (selectedFile) {
    return (
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center bg-primary/10 rounded-lg">
              <File className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="font-medium">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
          {onFileRemove && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onFileRemove}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </Card>
    );
  }

  return (
    <Card
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed border-muted-foreground/25 hover:border-primary/50 transition-colors cursor-pointer",
        isDragActive && "border-primary bg-primary/5"
      )}
    >
      <div className="p-8 text-center">
        <input {...getInputProps({ accept: ACCEPT_EXTS })} />
        <div className="flex flex-col items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center bg-primary/10 rounded-lg">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold">
              {isDragActive ? "Drop your file here" : "Upload your data file"}
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              Drag and drop or click to browse
            </p>
            <p className="text-xs text-muted-foreground mt-2">
              Supports PDF, PNG, JPG, PPTX, XLSX, DOCX, CSV, TXT (≤10MB)
            </p>
          </div>
          <Button variant="outline" type="button">
            <Upload className="h-4 w-4 mr-2" />
            Choose File
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default FileUpload;