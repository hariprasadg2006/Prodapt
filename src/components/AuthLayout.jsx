import Logo from "./Logo.jsx";
import AuthIllustration from "./AuthIllustration.jsx";

export default function AuthLayout({ children, illustration }) {
  return (
    <div className="auth-shell">
      <div className="auth-shell__form">
        <div className="auth-shell__form-inner">
          <Logo />
          {children}
        </div>
      </div>
      <div className="auth-shell__side">
        <AuthIllustration {...illustration} />
      </div>
    </div>
  );
}
