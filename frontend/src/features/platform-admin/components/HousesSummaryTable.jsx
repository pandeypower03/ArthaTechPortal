import Card from "../../../components/ui/Card.jsx";
import Chip from "../../../components/ui/Chip.jsx";
import Table, { TwoLine } from "../../../components/ui/Table.jsx";
import { formatDate, formatDateTime } from "../../../lib/dates.js";
import { formatShort } from "../../../lib/money.js";
import { PLANS } from "../labels.js";

export default function HousesSummaryTable({ houses, projects, users }) {
  const columns = [
    {
      header: "House",
      render: (h) => (
        <TwoLine
          main={h.name}
          sub={`${h.city} · Since ${formatDate(h.createdAt)}`}
        />
      ),
    },
    {
      header: "Plan",
      render: (h) => (
        <TwoLine
          main={PLANS[h.plan]}
          sub={`${formatShort(h.monthlyFeePaise)} a month`}
        />
      ),
    },
    {
      header: "Status",
      render: (h) =>
        h.status === "active" ? (
          <Chip tone="green">Active</Chip>
        ) : (
          <Chip tone="red">Suspended</Chip>
        ),
    },
    {
      header: "Projects",
      align: "right",
      render: (h) => projects.filter((p) => p.houseId === h.id).length,
    },
    {
      header: "Users",
      align: "right",
      render: (h) => users.filter((u) => u.houseId === h.id).length,
    },
    {
      header: "Last activity",
      render: (h) => (
        <TwoLine
          main={formatDateTime(h.lastActivity.at)}
          sub={h.lastActivity.action}
        />
      ),
    },
  ];

  return (
    <Card title="Production houses">
      <Table columns={columns} rows={houses} getKey={(h) => h.id} />
    </Card>
  );
}
