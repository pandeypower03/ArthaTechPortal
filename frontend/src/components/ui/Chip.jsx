const tones = {
  grey: "bg-panel text-ink-2",
  green: "bg-ok-wash text-ok",
  amber: "bg-warn-wash text-warn",
  red: "bg-bad-wash text-bad",
  blue: "bg-panel text-brand-deep",
  dark: "bg-brand text-white",
};

export default function Chip({ tone = "grey", children }) {
  return (
    <span
      className={`inline-flex items-center whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-semibold ${tones[tone]}`}
    >
      {children}
    </span>
  );
}
