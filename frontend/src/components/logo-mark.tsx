export function LogoMark({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <rect width="32" height="32" rx="6" fill="#050807" stroke="rgba(34,197,94,0.2)" />
      <path
        fill="#22c55e"
        d="M16 4.5v3.2c-3.9.2-6.6 2.1-6.6 5.4 0 2.6 1.5 4.1 5.1 5.2l2.2.7c2.6.8 3.5 1.5 3.5 2.9 0 1.7-1.5 2.7-3.9 2.7-2.1 0-3.7-.8-4.4-2.3l-.3-.7-3.1 1.1.2.6c1.1 2.8 3.7 4.3 7.6 4.5V28.5h2.8v-3.1c3.6-.3 6.2-2.2 6.2-5.4 0-2.8-1.7-4.3-5.4-5.5l-2.1-.7c-2.4-.7-3.3-1.4-3.3-2.8 0-1.6 1.4-2.6 3.7-2.6 1.9 0 3.3.7 3.9 2l.3.6 3-.9-.2-.6C22.6 6.6 20.1 5 16.4 4.8V4.5H16z"
      />
    </svg>
  );
}
