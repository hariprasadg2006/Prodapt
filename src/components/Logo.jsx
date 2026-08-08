export default function Logo({ variant = "dark" }) {
  return (
    <div className={`logo logo--${variant}`}>
      <span className="logo__mark" aria-hidden="true">
        <svg viewBox="0 0 28 28" width="24" height="24" fill="none">
          <circle cx="14" cy="14" r="3.2" fill="currentColor" />
          <circle cx="5" cy="6" r="2.1" fill="currentColor" opacity="0.55" />
          <circle cx="23" cy="7" r="2.1" fill="currentColor" opacity="0.55" />
          <circle cx="6" cy="22" r="2.1" fill="currentColor" opacity="0.55" />
          <circle cx="22" cy="21" r="2.1" fill="currentColor" opacity="0.55" />
          <path
            d="M14 14 L5 6 M14 14 L23 7 M14 14 L6 22 M14 14 L22 21"
            stroke="currentColor"
            strokeWidth="1.1"
            opacity="0.5"
          />
        </svg>
      </span>
      <span className="logo__word">
        Research<strong>AI</strong>
      </span>
    </div>
  );
}
