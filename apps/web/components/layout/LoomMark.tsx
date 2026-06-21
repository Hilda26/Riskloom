export function LoomMark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#6366F1" />
        </linearGradient>
      </defs>
      <path d="M14 2 L22 9 L14 16 L6 9 Z" fill="none" stroke="url(#lg1)" strokeWidth="1.5" />
      <path d="M14 12 L22 19 L14 26 L6 19 Z" fill="none" stroke="url(#lg1)" strokeWidth="1.5" opacity={0.7} />
      <line x1="14" y1="2" x2="14" y2="26" stroke="url(#lg1)" strokeWidth="1" opacity={0.4} />
      <circle cx="14" cy="9" r="2.5" fill="url(#lg1)" />
      <circle cx="14" cy="19" r="2" fill="url(#lg1)" opacity={0.7} />
      <circle cx="6" cy="9" r="1.2" fill="#F59E0B" opacity={0.6} />
      <circle cx="22" cy="9" r="1.2" fill="#6366F1" opacity={0.6} />
    </svg>
  );
}
