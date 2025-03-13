"use client";

import { Card, Table, Offcanvas } from "react-bootstrap";
import { useState, useEffect } from "react";
import DocumentChat from "@/components/Dashboard/Chat";
import Pagination from "./Pagination";

const PerformanceOfAgents = () => {
  const [documents, setDocuments] = useState([]);
  const [showChat, setShowChat] = useState(false);
  const [selectedDocumentName, setSelectedDocumentName] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}docs`,
          {
            method: "GET",
            credentials: "include",
          }
        );
        if (!response.ok) {
          throw new Error("Failed to fetch documents");
        }
        const data = await response.json();
        setDocuments(data);
      } catch (error) {
        console.error("Error fetching documents:", error);
        setDocuments([]);
      }
    };

    loadData();
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    if (isNaN(date)) return 'Invalid date';

    const day = date.getDate();
    const month = date.toLocaleString('default', { month: 'long' }).toLowerCase();
    const year = date.getFullYear();

    let hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    const minutesStr = minutes < 10 ? `0${minutes}` : minutes;

    return `${day} ${month} ${year} at ${hours}:${minutesStr} ${ampm}`;
  };

  const handleChatClick = (docName) => {
    setSelectedDocumentName(docName);
    setShowChat(true);
  };

  const handleCloseChat = () => {
    setSelectedDocumentName(null);
    setTimeout(() => {
      setShowChat(false);
    }, 0);
  };

  const renderStatusBadge = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === "success") {
      return (
        <span className="bg-opacity-10 bg-success py-1 px-2 text-secondary rounded-1 fw-medium fs-12 badge bg-success">
          Success
        </span>
      );
    } else if (lowerStatus === "processing") {
      return (
        <span className="bg-opacity-10 bg-warning py-1 px-2 text-secondary rounded-1 fw-medium fs-12 badge bg-warning">
          Processing
        </span>
      );
    } else {
      return (
        <span className="bg-opacity-10 bg-danger py-1 px-2 text-secondary rounded-1 fw-medium fs-12 badge bg-danger">
          Failed
        </span>
      );
    }
  };

  return (
    <>
      <Card className="bg-white border-0 rounded-3 mb-4">
        <Card.Body className="p-0">
          <div className="p-4">
            <h3 className="mb-0">My Documents</h3>
          </div>

          <div className="default-table-area style-two all-projects">
            <div className="table-responsive">
              <Table className="align-middle">
                <thead>
                  <tr>
                    <th scope="col">ID</th>
                    <th scope="col">Document Name</th>
                    <th scope="col">Upload Date</th>
                    <th scope="col">Status</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.length > 0 ? (
                    documents.map((doc) => (
                      <tr key={doc.id}>
                        <td className="text-body">{doc.id}</td>
                        <td>{doc.file_name}</td>
                        <td>{formatDate(doc.created_at)}</td>
                        <td>{renderStatusBadge(doc.status)}</td>
                        <td>
                          <div className="d-flex align-items-center gap-1">
                            {doc.status?.toLowerCase() === "success" && (
                              <button 
                                type="button"
                                className="btn btn-outline-success d-flex align-items-center gap-2"
                                onClick={() => handleChatClick(doc.id)}
                              >
                                <span className="material-symbols-outlined fs-16 text-success">
                                  chat
                                </span>
                                Chat
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="text-center">
                        No documents found
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </div>
            <Pagination />
          </div>
        </Card.Body>
      </Card>

      <Offcanvas show={showChat} onHide={handleCloseChat} placement="end" className="w-50">
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>Chat for Document {selectedDocumentName}</Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>
          {showChat && selectedDocumentName && <DocumentChat documentId={selectedDocumentName} key={selectedDocumentName} />}
        </Offcanvas.Body>
      </Offcanvas>

    </>
  );
};

export default PerformanceOfAgents;
