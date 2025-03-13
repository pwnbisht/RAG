"use client"

import { Row } from "react-bootstrap";
import { useRouter } from "next/navigation";
import PerformanceOfAgents from "@/components/Dashboard/DocumentTable";

export default function Page() {
  const router = useRouter();

  const handleAddDocument = () => {
    router.push("/documents/add");
  };

  return (
    <> 
      <div className='d-flex justify-content-end align-items-center mb-4 mt-4'>
        <button
          type="button"
          onClick={handleAddDocument}
          className="bg-success bg-opacity-10 fw-medium text-success py-2 px-4 btn btn-lg btn-success"
        >
          <i className="ri-add-line"></i> Add Documents
        </button>
      </div>
      <Row>
        <PerformanceOfAgents />
      </Row> 
    </>
  );
}
