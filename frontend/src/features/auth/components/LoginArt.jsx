const FLOW = [
  "Team plan",
  "Auditor records",
  "Approval",
  "Accounts",
  "Finance",
  "Paid",
];

export default function LoginArt() {
  return (
    <section className="flex flex-col justify-between gap-8 bg-brand px-5 py-7 text-white md:px-11 md:py-12">
      <div className="flex items-center gap-2.5 font-display text-[17px] font-bold">
        <span className="grid size-7.5 place-items-center rounded-lg bg-accent text-sm font-extrabold text-ink">
          FB
        </span>
        Film Budget Platform
      </div>

      <div className="grid gap-4.5">
        <h1 className="max-w-[14ch] text-[32px] leading-[1.05] font-bold md:text-[42px]">
          Every rupee of the film, checked before it is paid.
        </h1>
        <p className="max-w-[46ch] text-base text-[#d3e4e1]">
          See what is budgeted, promised and spent at any moment. Every day
          sheet and bill passes the same checks, with a name and a date on each
          step.
        </p>
        <div className="flex flex-wrap items-center gap-1.5 text-[13px]">
          {FLOW.map((step, index) => (
            <span key={step} className="flex items-center gap-1.5">
              <span className="rounded-full bg-white/15 px-2.5 py-1">
                {step}
              </span>
              {index < FLOW.length - 1 && (
                <i className="not-italic opacity-60">→</i>
              )}
            </span>
          ))}
        </div>
      </div>

      <p className="text-[13px] text-[#d3e4e1]">
        Money control for film productions.
      </p>
    </section>
  );
}
