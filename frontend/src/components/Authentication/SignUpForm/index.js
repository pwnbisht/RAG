"use client";

import { useState } from "react";
import { useRouter } from "next/navigation"; 
import { Row, Col, Form } from "react-bootstrap";
import Link from "next/link";
import Image from "next/image";
import { useForm } from "react-hook-form";
import { signupUser } from "./signupservice";

const SignUpForm = () => {

  const [errorMsg, setErrorMsg] = useState("");
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    try {
      const result = await signupUser(data);
      setErrorMsg(""); 
      router.push("/auth/sign-in");
    } catch (error) {
      setErrorMsg(error.message || "Signup failed. Please try again.");
    }
  };

  return (
    <>
      <div className="auth-main-content m-auto m-1230 px-3">
        <Row className="align-items-center">
          <Col lg={6} className="d-none d-lg-block">
            <Image
              src="/images/register.jpg"
              className="rounded-3"
              alt="register"
              width={646}
              height={804}
            />
          </Col>

          <Col lg={6}>
            <div className="mw-480 ms-lg-auto">
              
              <h3 className="fs-28 mb-2">Sign up to Voice AI</h3>
              <p className="fw-medium fs-16 mb-4">
                Sign up with social account or enter your details
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
                <Form.Group className="mb-3">
                  <label className="label text-secondary">Username</label>
                  <Form.Control
                    type="text"
                    className="h-55"
                    placeholder="jhondoe"
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

                <Form.Group className="mb-3">
                  <label className="label text-secondary">Email Address</label>
                  <Form.Control
                    type="email"
                    className="h-55"
                    placeholder="example@xyz.com"
                    {...register("email", {
                      required: "Email is required",
                      pattern: {
                        value: /^\S+@\S+$/i,
                        message: "Invalid email address",
                      },
                    })}
                  />
                  {errors.email && (
                    <span className="text-danger">{errors.email.message}</span>
                  )}
                </Form.Group>

                <Form.Group className="mb-3">
                  <label className="label text-secondary">Password</label>
                  <Form.Control
                    type="password"
                    className="h-55"
                    placeholder="Type password"
                    {...register("password", {
                      required: "Password is required",
                      minLength: {
                        value: 6,
                        message: "Password must be at least 6 characters long.",
                      },
                      pattern: {
                        value: /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/,
                        message:
                          "Password must contain at least one uppercase letter, one number, and one special character.",
                      },
                    })}
                  />
                  {errors.password && (
                    <span className="text-danger">{errors.password.message}</span>
                  )}
                </Form.Group>

                <Form.Group className="mb-3">
                  <button
                    type="submit"
                    className="btn btn-primary fw-medium py-2 px-3 w-100"
                  >
                    <div className="d-flex align-items-center justify-content-center py-1">
                      <span className="material-symbols-outlined fs-20 text-white me-2">
                        person_4
                      </span>
                      <span>Sign Up</span>
                    </div>
                  </button>
                </Form.Group>

                <Form.Group>
                  <p>By confirming your email, you agree to our <Link href="/terms-conditions" className="fw-medium text-decoration-none">Terms of Service</Link> and that you have read and understood our <Link href="/privacy-policy" className="fw-medium text-decoration-none">Privacy Policy</Link>.</p>

                  <p>Already have an account. <Link href="/auth/sign-in/" className="fw-medium text-primary text-decoration-none">Sign In</Link></p>
                </Form.Group>
              </Form>
            </div>
          </Col>
        </Row>
      </div>
    </>
  );
};

export default SignUpForm;
