"use client";

import { useState } from "react";
import { useRouter } from "next/navigation"; 
import { Row, Col, Form } from "react-bootstrap";
import Link from "next/link";
import Image from "next/image";
import { useForm } from "react-hook-form";
import { loginUser } from "./loginservice";


const SignInForm = () => {
  const [errorMsg, setErrorMsg] = useState("");
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  // This function runs when the form is valid and submitted
  const onSubmit = async (data) => {
    try {
      const result = await loginUser(data);
      setErrorMsg(""); 
      router.push("/");
    } catch (error) {
      setErrorMsg(error.message || "Login failed. Please try again.");
    }
  };

  return (
    <>
      <div className="auth-main-content m-auto m-1230 px-3">
        <Row className="align-items-center">
          <Col lg={6} className="d-none d-lg-block">
            <Image
              src="/images/login.jpg"
              className="rounded-3"
              alt="login"
              width={646}
              height={804}
            />
          </Col>

          <Col lg={6}>
            <div className="mw-480 ms-lg-auto">
              <h3 className="fs-28 mb-2">Welcome back to Voice AI!</h3>
              <p className="fw-medium fs-16 mb-4">
                Sign In with social account or enter your details
              </p>

              {errorMsg && (
                <div className="alert alert-danger" role="alert">
                  {errorMsg}
                </div>
              )}

              <div className="row justify-content-center">
                <div className="col-lg-4 col-sm-4">
                  <a
                    href="https://www.google.com/"
                    target="_blank"
                    className="btn btn-outline-secondary bg-transparent w-100 py-2 hover-bg mb-4"
                    style={{
                      borderColor: "#D6DAE1",
                    }}
                  >
                    <Image
                      src="/images/google.svg"
                      alt="google"
                      width={25}
                      height={25}
                    />
                  </a>
                </div>

                <div className="col-lg-4 col-sm-4">
                  <a
                    href="https://www.facebook.com/"
                    target="_blank"
                    className="btn btn-outline-secondary bg-transparent w-100 py-2 hover-bg mb-4"
                    style={{
                      borderColor: "#D6DAE1",
                    }}
                  >
                    <Image
                      src="/images/facebook2.svg"
                      alt="facebook2"
                      width={25}
                      height={25}
                    />
                  </a>
                </div>

                <div className="col-lg-4 col-sm-4">
                  <a
                    href="https://www.apple.com/"
                    target="_blank"
                    className="btn btn-outline-secondary bg-transparent w-100 py-2 hover-bg mb-4"
                    style={{
                      borderColor: "#D6DAE1",
                    }}
                  >
                    <Image
                      src="/images/apple.svg"
                      alt="apple"
                      width={25}
                      height={25}
                    />
                  </a>
                </div>
              </div>

              <Form onSubmit={handleSubmit(onSubmit)}>
                <Form.Group className="mb-4">
                  <label className="label text-secondary">Username</label>
                  <Form.Control
                    type="text"
                    className="h-55"
                    placeholder="jhoncena"
                    {...register("username", {
                      required: "Username is required",
                      pattern: {
                        value: /^[a-zA-Z0-9_]{3,}$/,
                        message:
                          "Invalid username. Use only letters, numbers, and underscores (min 3 characters).",
                      },
                    })}
                  />
                  {errors.username && (
                    <span className="text-danger">{errors.username.message}</span>
                  )}
                </Form.Group>

                <Form.Group className="mb-4">
                  <label className="label text-secondary">Password</label>
                  <Form.Control
                    type="password"
                    className="h-55"
                    placeholder="Type password"
                    {...register("password", {
                      required: "Password is required",
                    })}
                  />
                  {errors.password && (
                    <span className="text-danger">{errors.password.message}</span>
                  )}
                </Form.Group>

                <Form.Group className="mb-4">
                  <Link href='/authentication/forgot-password/' className="fw-medium text-primary text-decoration-none">
                    Forgot Password?
                  </Link>
                </Form.Group>

                <Form.Group className="mb-4">
                  <button
                    type="submit"
                    className="btn btn-primary fw-medium py-2 px-3 w-100"
                  >
                    <div className="d-flex align-items-center justify-content-center py-1">
                      <span className="material-symbols-outlined fs-20 text-white me-2">
                        login
                      </span>
                      <span>Sign In</span>
                    </div>
                  </button>
                </Form.Group>

                <Form.Group>
                  <p>
                    Don’t have an account.{" "}
                    <Link
                      href="/auth/sign-up/"
                      className="fw-medium text-primary text-decoration-none"
                    >
                      Sign Up
                    </Link>
                  </p>
                </Form.Group>
              </Form>
            </div>
          </Col>
        </Row>
      </div>
    </>
  );
};

export default SignInForm;
