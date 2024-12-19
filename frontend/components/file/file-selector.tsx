'use client';

import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue, 
} from "@/components/ui/select";
import { useFileStore } from "@/store/file-store";

export function FileSelector() {
  const { files, selectedFile, setSelectedFile } = useFileStore();

  return (
    <Select
      value={selectedFile?.id || ""}
      onValueChange={(value) => {
        const file = files.find(f => f.id === value);
        setSelectedFile(file || null);
      }}
    >
      <SelectTrigger className="w-full">
        <SelectValue placeholder="Select a file" />
      </SelectTrigger>
      <SelectContent>
        {files.map((file) => (
          <SelectItem
            key={file.id}
            value={file.id}
            className="cursor-pointer"
          >
            {file.filename}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}