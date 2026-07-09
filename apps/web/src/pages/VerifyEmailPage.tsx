import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { FaCheckCircle, FaExclamationTriangle } from "react-icons/fa";

import { verifyEmail } from "../api/auth";

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Verifying your email...");

  useEffect(() => {
    const token = searchParams.get("token") || "";
    if (!token) {
      setStatus("error");
      setMessage("Verification token is missing.");
      return;
    }

    verifyEmail(token)
      .then((result) => {
        setStatus("success");
        setMessage(result.message || "Email verified successfully.");
        window.setTimeout(() => navigate("/login", { replace: true }), 2200);
      })
      .catch((error: Error) => {
        setStatus("error");
        setMessage(error.message || "Verification failed.");
      });
  }, [navigate, searchParams]);

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className={`auth-icon-large ${status}`}>
          {status === "error" ? <FaExclamationTriangle /> : <FaCheckCircle />}
        </div>
        <div className="auth-heading compact">
          <p className="eyebrow">Email verification</p>
          <h1>{status === "success" ? "Verified" : status === "error" ? "Could not verify" : "Verifying"}</h1>
        </div>
        <p className="auth-copy">{message}</p>
        {status === "success" && <p className="muted-text">Redirecting to login...</p>}
        {status === "error" && <Link className="btn btn-primary auth-submit" to="/register">Create account again</Link>}
      </section>
    </main>
  );
}
