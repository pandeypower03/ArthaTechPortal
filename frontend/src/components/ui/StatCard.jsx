export default function StatCard({ label, value, note, hero = false }) {
  const box = hero
    ? "border-brand bg-brand text-white"
    : "border-line bg-white text-ink";
  const small = hero ? "text-[#cfe0dd]" : "text-brand-soft";

  return (
    <div
      className={`grid content-start gap-0.5 rounded-[10px] border px-4 py-3.5 ${box}`}
    >
      <span
        className={`text-xs font-semibold uppercase tracking-wider ${small}`}
      >
        {label}
      </span>
      <strong className="font-display text-[25px] font-bold tabular-nums">
        {value}
      </strong>
      {note && <small className={`text-[12.5px] ${small}`}>{note}</small>}
    </div>
  );
}
