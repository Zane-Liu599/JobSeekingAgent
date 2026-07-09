import { FormEvent, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaEnvelope, FaLock, FaPhone, FaUserPlus, FaUser } from "react-icons/fa";

import { passwordChecks, passwordStrength, phoneValidationMessage, registerAccount } from "../api/auth";

export function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "" });
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const strength = useMemo(() => passwordStrength(form.password), [form.password]);
  const checks = useMemo(() => passwordChecks(form.password), [form.password]);
  const phoneError = useMemo(() => phoneValidationMessage(form.phone), [form.phone]);
  const canSubmit = !phoneError && !isBusy;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setMessage("");
    if (phoneError) {
      setMessage(phoneError);
      return;
    }
    setIsBusy(true);
    try {
      const result = await registerAccount(form);
      navigate("/verify-pending", {
        replace: true,
        state: { email: result.email }
      });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Registration failed");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card auth-card-wide">
        <div className="auth-heading">
          <span className="brand-mark">JSA</span>
          <div>
            <p className="eyebrow">Start applying smarter</p>
            <h1>Create account</h1>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Full name
            <span className="input-with-icon">
              <FaUser />
              <input
                required
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                placeholder="Your name"
              />
            </span>
          </label>
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
            Phone
            <span className="input-with-icon">
              <FaPhone />
              <input
                required
                inputMode="tel"
                value={form.phone}
                onChange={(event) => setForm({ ...form, phone: event.target.value })}
                placeholder="+61 400 000 000"
              />
            </span>
            {form.phone && phoneError && <small className="field-error">{phoneError}</small>}
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
                placeholder="Use a strong password"
              />
            </span>
          </label>

          <div className={`password-meter score-${strength.score}`}>
            <div className="password-meter-bar"><span /></div>
            <strong>{strength.label}</strong>
          </div>
          <div className="password-checks">
            {checks.map((item) => (
              <span key={item.label} className={item.passed ? "passed" : ""}>{item.label}</span>
            ))}
          </div>

          {message && <div className="auth-alert">{message}</div>}
          <button className="btn btn-primary auth-submit" disabled={!canSubmit} type="submit">
            <FaUserPlus /> {isBusy ? "Creating account" : "Register"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </section>
    </main>
  );
}
