// A white box with an optional header (title on the left, actions on the right).
export default function Card({ title, subtitle, actions, children }) {
  return (
    <section className="min-w-0 rounded-[10px] border border-line bg-white">
      {(title || actions) && (
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4.5 py-3.5">
          <div>
            {title && <h2 className="text-lg font-semibold">{title}</h2>}
            {subtitle && (
              <p className="text-[12.5px] text-brand-soft">{subtitle}</p>
            )}
          </div>
          {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
        </header>
      )}
      {children}
    </section>
  );
}
