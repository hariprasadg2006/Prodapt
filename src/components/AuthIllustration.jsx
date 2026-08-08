const CHIPS = [
  { label: "arXiv:24.0819", top: "14%", left: "8%", delay: "0s" },
  { label: "cited by 128", top: "68%", left: "4%", delay: "0.6s" },
  { label: "Fig. 3 — results", top: "22%", left: "62%", delay: "1.1s" },
  { label: "source verified", top: "78%", left: "58%", delay: "0.3s" },
];

export default function AuthIllustration({ eyebrow, headline, body }) {
  return (
    <div className="illustration">
      <div className="illustration__grid" aria-hidden="true" />

      <svg
        className="illustration__graph"
        viewBox="0 0 480 480"
        fill="none"
        aria-hidden="true"
      >
        <g className="illustration__triangle">
          <polygon points="60,40 220,40 140,180" />
          <polygon points="220,40 380,40 300,180" />
          <polygon points="140,180 300,180 220,320" />
        </g>
        <g stroke="rgba(255,255,255,0.28)" strokeWidth="1.2">
          <line x1="240" y1="220" x2="120" y2="120" />
          <line x1="240" y1="220" x2="360" y2="100" />
          <line x1="240" y1="220" x2="90" y2="300" />
          <line x1="240" y1="220" x2="330" y2="330" />
          <line x1="240" y1="220" x2="230" y2="360" />
          <line x1="120" y1="120" x2="360" y2="100" />
          <line x1="90" y1="300" x2="230" y2="360" />
        </g>
        <g>
          <circle className="node node--core" cx="240" cy="220" r="10" />
          <circle className="node" cx="120" cy="120" r="6" />
          <circle className="node" cx="360" cy="100" r="5" />
          <circle className="node" cx="90" cy="300" r="6" />
          <circle className="node" cx="330" cy="330" r="5" />
          <circle className="node" cx="230" cy="360" r="6" />
        </g>
      </svg>

      {CHIPS.map((chip) => (
        <span
          key={chip.label}
          className="illustration__chip"
          style={{ top: chip.top, left: chip.left, animationDelay: chip.delay }}
        >
          {chip.label}
        </span>
      ))}

      <div className="illustration__copy">
        <span className="illustration__eyebrow">{eyebrow}</span>
        <h2 className="illustration__headline">{headline}</h2>
        <p className="illustration__body">{body}</p>
      </div>
    </div>
  );
}
