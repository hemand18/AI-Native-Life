export default function Logo({ size = 32, showText = true }) {
  return (
    <span className="logo">
      <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
        <defs>
          <linearGradient id="logo-g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#2F5BFF" />
            <stop offset="1" stopColor="#6A3DFF" />
          </linearGradient>
        </defs>
        <rect width="64" height="64" rx="16" fill="url(#logo-g)" />
        <circle cx="32" cy="32" r="13" fill="none" stroke="#fff" strokeWidth="4" />
        <circle cx="32" cy="32" r="4.5" fill="#fff" />
        <circle className="logo-node" cx="48" cy="20" r="5.5" fill="#FF6B57" />
      </svg>
      {showText && <span className="logo-text">AI-Native Life</span>}
    </span>
  );
}
