import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../features/auth/useAuth.js";
import Button from "../ui/Button.jsx";

function initials(name) {
  return name
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

// Teal rail on the left (on top on phones), work area on the right.
// nav: [{ to, label, end? }]
export default function AppShell({ roleLabel, nav }) {
  const { user, signOut } = useAuth();
  const name = user.full_name || user.username;

  return (
    <div className="grid min-h-full grid-cols-[minmax(0,1fr)] grid-rows-[auto_1fr] md:grid-cols-[240px_minmax(0,1fr)] md:grid-rows-none">
      <aside className="flex min-w-0 flex-col gap-2.5 bg-brand px-4 py-3 text-white md:sticky md:top-0 md:h-screen md:gap-5.5 md:overflow-y-auto md:px-3.5 md:py-5">
        <div className="flex items-center gap-2.5 px-2 font-display text-[17px] font-bold">
          <span className="grid size-7.5 place-items-center rounded-lg bg-accent text-sm font-extrabold text-ink">
            FB
          </span>
          Film Budget Platform
        </div>

        <p className="px-2 text-xs tracking-widest text-line uppercase">
          {roleLabel}
        </p>

        <nav className="flex gap-1.5 overflow-x-auto pb-1 md:flex-col md:gap-0.75 md:pb-0">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `rounded-lg px-2.5 py-2.25 text-sm font-semibold whitespace-nowrap ${
                  isActive
                    ? "bg-canvas text-brand-deep"
                    : "text-white hover:bg-white/15"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto hidden gap-2 px-2 text-[12.5px] text-line md:grid">
          <span>Signed in as {name}</span>
          <button
            type="button"
            onClick={signOut}
            className="cursor-pointer rounded-lg border border-white/40 bg-transparent px-2.5 py-1.5 text-[13px] font-semibold text-white hover:bg-white/15"
          >
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-col">
        <header className="sticky top-0 z-5 flex flex-wrap items-center justify-between gap-3 border-b border-line bg-canvas px-4 py-2.5 md:px-7">
          <div className="flex items-center gap-2.5">
            <span className="grid size-8 place-items-center rounded-full bg-panel text-[13px] font-bold text-brand-deep">
              {initials(name)}
            </span>
            <div className="leading-tight">
              <b className="block text-sm">{name}</b>
              <small className="text-brand-soft">{roleLabel}</small>
            </div>
          </div>
          <div className="flex items-center gap-2.5">
            <span className="rounded-full bg-panel px-2.5 py-0.75 text-xs text-ink-2">
              Demo data
            </span>
            <Button size="small" className="md:hidden" onClick={signOut}>
              Sign out
            </Button>
          </div>
        </header>

        <main className="grid w-full max-w-[1280px] content-start gap-5.5 px-4 pt-4.5 pb-12 md:px-7 md:pt-6.5 md:pb-15">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
