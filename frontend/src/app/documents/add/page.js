"use client";
 
import MultiFileUpload from '@/components/Dashboard/FileUpload';

export default function Page() {
  return (
    <>
      <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-4">
        <h3 className="mb-0">Select and Upload Files</h3>
      </div>

      <MultiFileUpload />
    </>
  );
}