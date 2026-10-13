import { useEffect } from "react";

export default function Modal({ title, onClose, children }) {
  useEffect(() => {
    function onKey(event) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-ink/50 p-4"
      onMouseDown={(event) => event.target === event.currentTarget && onClose()}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="max-h-full w-full max-w-145 overflow-auto rounded-2xl bg-canvas shadow-2xl"
      >
        <header className="sticky top-0 flex items-center justify-between border-b border-line bg-canvas px-4.5 py-3.5">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="cursor-pointer rounded-md px-2 py-1 text-[22px] leading-none text-ink-2 hover:bg-panel"
          >
            ×
          </button>
        </header>
        <div className="p-4.5">{children}</div>
      </div>
    </div>
  );
}
