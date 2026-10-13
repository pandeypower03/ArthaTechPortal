const control =
  "w-full min-w-0 rounded-lg border border-line bg-white px-2.5 py-2 text-[14.5px] text-ink focus:border-brand focus:outline-2 focus:outline-panel";

// Label above a form control. Use with Input, Select or Textarea below.
export function Field({ label, hint, children }) {
  return (
    <label className="mb-3 grid gap-1 text-[13.5px] font-semibold">
      <span>{label}</span>
      {children}
      {hint && (
        <small className="text-[12.5px] font-normal text-brand-soft">
          {hint}
        </small>
      )}
    </label>
  );
}

export function Input({ className = "", ...props }) {
  return <input className={`${control} ${className}`} {...props} />;
}

export function Select({ options, className = "", ...props }) {
  return (
    <select className={`${control} ${className}`} {...props}>
      {options.map(([value, label]) => (
        <option key={value} value={value}>
          {label}
        </option>
      ))}
    </select>
  );
}

export function Textarea({ className = "", ...props }) {
  return <textarea rows={3} className={`${control} ${className}`} {...props} />;
}
