// Shows "Loading" or an error, then calls children(data) when the data is ready.
// state comes from useLoad().
export default function Async({ state, children }) {
  if (state.loading) return <p className="py-6 text-brand-soft">Loading…</p>;
  if (state.error) {
    return (
      <p role="alert" className="rounded-lg bg-bad-wash px-3 py-2 text-bad">
        Something went wrong. Please try again.
      </p>
    );
  }
  return children(state.data);
}
