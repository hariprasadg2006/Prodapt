import { useState } from "react";
import AuthLayout from "./AuthLayout.jsx";
import FormInput from "./FormInput.jsx";
import PasswordInput from "./PasswordInput.jsx";
import { validateSignIn } from "../utils/validation.js";

export default function SignIn({ onSignedIn, onGoToSignUp }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [forgotNote, setForgotNote] = useState(false);

  function handleChange(field) {
    return (e) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    };
  }

  function handleSubmit(e) {
    e.preventDefault();
    const nextErrors = validateSignIn(form);
    setErrors(nextErrors);

    // Frontend-only: no request is sent anywhere. A valid form just
    // moves the user on to the placeholder dashboard.
    if (Object.keys(nextErrors).length === 0) {
      onSignedIn(form.email);
    }
  }

  return (
    <AuthLayout
      illustration={{
        eyebrow: "Knowledge graph",
        headline: "Pick up your research exactly where you left it.",
        body: "Every source, summary, and citation stays connected across sessions.",
      }}
    >
      <h1 className="auth-heading">Welcome back</h1>
      <p className="auth-subtitle">Continue your research with AI</p>

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <FormInput
          id="signin-email"
          label="Email address"
          type="email"
          value={form.email}
          onChange={handleChange("email")}
          error={errors.email}
          placeholder="you@lab.edu"
          autoComplete="email"
        />

        <PasswordInput
          id="signin-password"
          label="Password"
          value={form.password}
          onChange={handleChange("password")}
          error={errors.password}
          placeholder="Enter your password"
          autoComplete="current-password"
        />

        <div className="auth-form__row">
          <button
            type="button"
            className="link-button"
            onClick={() => setForgotNote(true)}
          >
            Forgot password?
          </button>
        </div>

        {forgotNote && (
          <p className="auth-note" role="status">
            This is a UI demo — password reset isn't wired to a backend yet.
          </p>
        )}

        <button type="submit" className="btn-primary">
          Sign In
        </button>
      </form>

      <p className="auth-switch">
        Don't have an account?{" "}
        <button type="button" className="link-button link-button--strong" onClick={onGoToSignUp}>
          Sign Up
        </button>
      </p>
    </AuthLayout>
  );
}
