import { create } from 'zustand';
import { FileResponse } from '@/types/file';

interface FileStore {
  selectedFile: FileResponse | null;
  files: FileResponse[];
  setSelectedFile: (file: FileResponse | null) => void;
  setFiles: (files: FileResponse[]) => void;
  addFile: (file: FileResponse) => void;
  removeFile: (fileId: string) => void;
}

export const useFileStore = create<FileStore>((set) => ({
  selectedFile: null,
  files: [],
  setSelectedFile: (file) => set({ selectedFile: file }),
  setFiles: (files) => set({ files }),
  addFile: (file) => set((state) => ({ files: [...state.files, file] })),
  removeFile: (fileId) =>
    set((state) => ({ files: state.files.filter((f) => f.id !== fileId) })),
}));