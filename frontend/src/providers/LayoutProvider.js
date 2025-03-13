"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";
import LeftSidebar from "@/components/Layout/LeftSidebar";
import TopNavbar from "@/components/Layout/TopNavbar";
import Footer from "@/components/Layout/Footer";
import ControlPanel from "@/components/Layout/ControlPanel";

const LayoutProvider = ({ children }) => {
  const [active, setActive] = useState(false);
  const pathname = usePathname();

  const toogleActive = () => {
    setActive(!active);
  };
  return (
    <>
      <div className={`main-wrapper-content ${active && "active"}`}>
        {!(
          pathname === "/auth/sign-in/" ||
          pathname === "/auth/sign-up/" ||

          pathname === "/authentication/sign-in/" ||
          pathname === "/authentication/sign-up/" ||
          pathname === "/authentication/forgot-password/" ||
          pathname === "/authentication/reset-password/" ||
          pathname === "/authentication/lock-screen/" ||
          pathname === "/authentication/confirm-email/" ||
          pathname === "/authentication/logout/"
        ) && (
          <>
            <LeftSidebar toogleActive={toogleActive} />
          </>
        )}

        <div className="main-content d-flex flex-column">
          {!(
            pathname === "/auth/sign-in/" ||
            pathname === "/auth/sign-up/" ||

            pathname === "/authentication/sign-in/" ||
            pathname === "/authentication/sign-up/" ||
            pathname === "/authentication/forgot-password/" ||
            pathname === "/authentication/reset-password/" ||
            pathname === "/authentication/lock-screen/" ||
            pathname === "/authentication/confirm-email/" ||
            pathname === "/authentication/logout/"
          ) && (
            <>
              <TopNavbar toogleActive={toogleActive} />
            </>
          )}

          {children}

          {!(
            pathname === "/auth/sign-in/" ||
            pathname === "/auth/sign-up/" ||
            
            pathname === "/authentication/sign-in/" ||
            pathname === "/authentication/sign-up/" ||
            pathname === "/authentication/forgot-password/" ||
            pathname === "/authentication/reset-password/" ||
            pathname === "/authentication/lock-screen/" ||
            pathname === "/authentication/confirm-email/" ||
            pathname === "/authentication/logout/"
          ) && <Footer />}
        </div>
      </div>
      
      <div
        style={{
          position: 'fixed',
          bottom: '0',
          right: '0',
          opacity: '0',
          visibility: 'hidden'
        }}
      >
        <ControlPanel />
      </div>
    </>
  );
};

export default LayoutProvider;
