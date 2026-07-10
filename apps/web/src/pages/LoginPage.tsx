import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaArrowLeft, FaEnvelope, FaLock, FaSignInAlt } from "react-icons/fa";

import { loginAccount } from "../api/auth";

export function LoginPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setMessage("");
    setIsBusy(true);
    try {
      await loginAccount(form.email, form.password);
      navigate("/app/profile-setup", { replace: true });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Login failed");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <Link className="auth-home-link" to="/">
          <FaArrowLeft /> Back to home
        </Link>
        <div className="auth-heading">
          <span className="brand-mark">JSA</span>
          <div>
            <p className="eyebrow">Welcome back</p>
            <h1>Log in</h1>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Email
            <span className="input-with-icon">
              <FaEnvelope />
              <input
                required
                type="email"
                value={form.email}
                onChange={(event) => setForm({ ...form, email: event.target.value })}
                placeholder="you@example.com"
              />
            </span>
          </label>
          <label>
            Password
            <span className="input-with-icon">
              <FaLock />
              <input
                required
                type="password"
                value={form.password}
                onChange={(event) => setForm({ ...form, password: event.target.value })}
                placeholder="Your password"
              />
            </span>
          </label>
          {message && <div className="auth-alert">{message}</div>}
          <button className="btn btn-primary auth-submit" disabled={isBusy} type="submit">
            <FaSignInAlt /> {isBusy ? "Logging in" : "Log in"}
          </button>
        </form>

        <p className="auth-switch">
          No account yet? <Link to="/register">Create one</Link>
        </p>
      </section>
    </main>
  );
}
