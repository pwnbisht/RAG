"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { Card, Form, Button, ListGroup, Spinner, Alert } from "react-bootstrap";

const MultiFileUpload = () => {
  const [files, setFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const router = useRouter();

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!files || files.length === 0) {
      setErrorMessage("No files selected.");
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}docs/upload`,
        {
          method: "POST",
          credentials: "include",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        setErrorMessage(errorData.message || "Upload failed.");
        return;
      }

      const data = await response.json();
      console.log("Upload success:", data);
      setFiles([]);
      router.push("/");
    } catch (error) {
      setErrorMessage("An error occurred during upload.");
      console.error("Upload error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="bg-white border-0 rounded-3 mb-4">
      <Card.Body className="p-4">
        <h5 className="fs-18 mb-4">Drag and drop your documents here</h5>
        <Form onSubmit={handleSubmit}>
          <div
            {...getRootProps()}
            className="form-control h-100 text-center position-relative p-4 p-lg-5"
            style={{
              cursor: "pointer",
              border: "2px dashed #ccc",
            }}
          >
            <input {...getInputProps()} />
            {isDragActive ? (
              <p>Drop the files here ...</p>
            ) : (
              <p>
                Drag and drop some files here, or click to select files
              </p>
            )}
          </div>

          {files && files.length > 0 && (
            <ListGroup className="mt-3">
              {files.map((file, index) => (
                <ListGroup.Item key={index}>
                  {file.name} - {(file.size / 1024).toFixed(2)} KB
                </ListGroup.Item>
              ))}
            </ListGroup>
          )}

          {errorMessage && (
            <Alert variant="danger" className="mt-3">
              {errorMessage}
            </Alert>
          )}

          <Button type="submit" className="mt-3" disabled={isLoading}>
            {isLoading ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Uploading...
              </>
            ) : (
              "Upload"
            )}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default MultiFileUpload;
