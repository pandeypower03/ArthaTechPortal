import StatCard from "../../../components/ui/StatCard.jsx";
import { formatShort } from "../../../lib/money.js";

export default function OverviewStats({ houses, projects, users }) {
  const activeHouses = houses.filter((h) => h.status === "active");
  const lockedUsers = users.filter((u) => u.locked).length;
  const monthlyEarnings = activeHouses.reduce(
    (sum, h) => sum + h.monthlyFeePaise,
    0,
  );

  return (
    <div className="grid grid-cols-[repeat(auto-fit,minmax(170px,1fr))] gap-3.5">
      <StatCard
        label="Production houses"
        value={houses.length}
        note={`${activeHouses.length} active`}
      />
      <StatCard
        label="Projects"
        value={projects.length}
        note="Across all houses"
      />
      <StatCard
        label="Users"
        value={users.length}
        note={`${lockedUsers} locked`}
      />
      <StatCard
        hero
        label="Monthly earnings"
        value={formatShort(monthlyEarnings)}
        note="Plan fees from active houses (assumed prices)"
      />
    </div>
  );
}
