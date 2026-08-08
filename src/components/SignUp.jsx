import { useState } from "react";
import AuthLayout from "./AuthLayout.jsx";
import FormInput from "./FormInput.jsx";
import PasswordInput from "./PasswordInput.jsx";
import { validateSignUp } from "../utils/validation.js";

export default function SignUp({ onSignedUp, onGoToSignIn }) {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [errors, setErrors] = useState({});

  function handleChange(field) {
    return (e) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    };
  }

  function handleSubmit(e) {
    e.preventDefault();
    const nextErrors = validateSignUp(form);
    setErrors(nextErrors);

    // Frontend-only: nothing is persisted or sent anywhere. A valid
    // form just moves the user on to the placeholder dashboard.
    if (Object.keys(nextErrors).length === 0) {
      onSignedUp(form.name);
    }
  }

  return (
    <AuthLayout
      illustration={{
        eyebrow: "Literature synthesis",
        headline: "Turn a stack of papers into one clear answer.",
        body: "ResearchAI reads, cross-references, and summarizes so you don't have to.",
      }}
    >
      <h1 className="auth-heading">Create your account</h1>
      <p className="auth-subtitle">Start researching smarter with AI</p>

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <FormInput
          id="signup-name"
          label="Full name"
          value={form.name}
          onChange={handleChange("name")}
          error={errors.name}
          placeholder="Ada Lovelace"
          autoComplete="name"
        />

        <FormInput
          id="signup-email"
          label="Email address"
          type="email"
          value={form.email}
          onChange={handleChange("email")}
          error={errors.email}
          placeholder="you@lab.edu"
          autoComplete="email"
        />

        <PasswordInput
          id="signup-password"
          label="Password"
          value={form.password}
          onChange={handleChange("password")}
          error={errors.password}
          placeholder="At least 8 characters"
          autoComplete="new-password"
          hint="Use 8 or more characters."
        />

        <button type="submit" className="btn-primary">
          Create Account
        </button>
      </form>

      <p className="auth-switch">
        Already have an account?{" "}
        <button type="button" className="link-button link-button--strong" onClick={onGoToSignIn}>
          Sign In
        </button>
      </p>
    </AuthLayout>
  );
}
