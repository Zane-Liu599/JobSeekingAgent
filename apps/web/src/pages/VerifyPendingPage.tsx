import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { FaEnvelopeOpenText, FaRedo } from "react-icons/fa";

import { resendVerificationEmail } from "../api/auth";

const resendCooldownSeconds = 60;

export function VerifyPendingPage() {
  const location = useLocation();
  const state = location.state as { email?: string } | null;
  const email = state?.email || "";
  const [secondsLeft, setSecondsLeft] = useState(resendCooldownSeconds);
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    if (secondsLeft <= 0) return undefined;
    const timer = window.setTimeout(() => setSecondsLeft((value) => value - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [secondsLeft]);

  async function handleResend() {
    if (!email || secondsLeft > 0) return;
    setMessage("");
    setIsBusy(true);
    try {
      const result = await resendVerificationEmail(email);
      setMessage(result.message);
      setSecondsLeft(result.retry_after_seconds || resendCooldownSeconds);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not resend verification email.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-icon-large"><FaEnvelopeOpenText /></div>
        <div className="auth-heading compact">
          <p className="eyebrow">Check your inbox</p>
          <h1>Verify your email</h1>
        </div>
        <p className="auth-copy">
          We sent a verification link to <strong>{email || "your email address"}</strong>.
          Open the link in that email to finish registration.
        </p>
        <button
          className="btn btn-outline-secondary auth-resend-button"
          disabled={!email || isBusy || secondsLeft > 0}
          onClick={handleResend}
          type="button"
        >
          <FaRedo />
          {isBusy
            ? "Resending"
            : secondsLeft > 0
              ? `Resend in ${secondsLeft}s`
              : "Resend verification email"}
        </button>
        {!email && (
          <p className="auth-copy compact">
            Open this page from registration so we know which email to resend to.
          </p>
        )}
        {message && <div className="auth-alert neutral">{message}</div>}
        <p className="auth-switch">
          Already verified? <Link to="/login">Back to login</Link>
        </p>
      </section>
    </main>
  );
}
