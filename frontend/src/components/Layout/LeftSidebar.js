"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Accordion } from "react-bootstrap";
import { usePathname } from "next/navigation";
import Link from "next/link";
import Image from "next/image";

import { logoutUser } from "./logoutservice"

const LeftSidebar = ({ toogleActive }) => {
  const pathname = usePathname();
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logoutUser();
      router.push("/auth/login/");
    } catch (error) {
      setErrorMsg(error.message || "Logout failed. Please try again.");
    }finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="sidebar-area">
        <div className="logo position-relative">
          <Link
            href="#"
            className="d-block text-decoration-none position-relative"
          >
            <Image
              src="/images/logo-icon.png"
              alt="logo-icon"
              width={26}
              height={26}
            />
            <span className="logo-text fw-bold text-dark">Voice AI</span>
          </Link>
          <button
            className="sidebar-burger-menu bg-transparent p-0 border-0 opacity-0 z-n1 position-absolute top-50 end-0 translate-middle-y"
            onClick={toogleActive}
          >
            <i className="material-symbols-outlined fs-24">close</i>
          </button>
        </div>

        <div className="sidebar-menu">
          <div className="menu-title small text-uppercase">
            <span className="menu-title-text">MAIN</span>
          </div>

          <Accordion defaultActiveKey="0" flush style={{ position: "relative", height: "100%" }}>
            <Accordion.Item eventKey="0">
              <Accordion.Header>
                <i className="material-symbols-outlined">dashboard</i>
                <span className="title">Dashboard</span>
              </Accordion.Header>
            </Accordion.Item>

            <div
              className="menu-item"
              style={{
                background: "#f11429",
                color: "white",
                borderRadius: "8px",
                position: "absolute",
                width: "100%",
                bottom: "10vh",
              }}
            >
              <button
                onClick={handleLogout}
                className="menu-link"
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "white",
                  width: "100%",
                }}
              >
                {loading ? (
                  <span>Loading...</span>
                ) : (
                  <>
                    <i className="material-symbols-outlined" style={{ color: "white" }}>
                      logout
                    </i>
                    <span className="title" style={{ color: "white" }}>
                      Logout
                    </span>
                  </>
                )}
              </button>
            </div>
          </Accordion>
        </div>
      </div>
    </>
  );
};

export default LeftSidebar;