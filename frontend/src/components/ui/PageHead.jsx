export default function PageHead({ title, text, actions }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-[28px] leading-tight font-bold">{title}</h1>
        {text && <p className="mt-1 max-w-[70ch] text-ink-2">{text}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}
