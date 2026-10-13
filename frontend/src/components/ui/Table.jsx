// columns: [{ header, render: (row) => node, align?: 'right' }]
export default function Table({
  columns,
  rows,
  getKey,
  empty = "Nothing to show.",
}) {
  if (rows.length === 0) {
    return <p className="px-4.5 py-6.5 text-center text-brand-soft">{empty}</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.header}
                className={`whitespace-nowrap bg-panel px-3 py-2.5 text-xs font-semibold uppercase tracking-wider text-ink-2 ${
                  col.align === "right" ? "text-right" : "text-left"
                }`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={getKey(row)}>
              {columns.map((col) => (
                <td
                  key={col.header}
                  className={`border-t border-panel px-3 py-2.5 align-middle ${
                    col.align === "right" ? "text-right whitespace-nowrap" : ""
                  }`}
                >
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// A bold line with a small grey line under it, used inside table cells.
export function TwoLine({ main, sub }) {
  return (
    <>
      <b className="font-semibold">{main}</b>
      {sub && (
        <span className="block text-[12.5px] text-brand-soft">{sub}</span>
      )}
    </>
  );
}
