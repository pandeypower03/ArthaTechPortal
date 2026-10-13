import Async from "../../../components/ui/Async.jsx";
import { useLoad } from "../../../lib/useLoad.js";
import { getOverview } from "../api.js";
import HousesSummaryTable from "./HousesSummaryTable.jsx";
import OverviewStats from "./OverviewStats.jsx";

export default function PlatformOverview() {
  const state = useLoad(getOverview);

  return (
    <Async state={state}>
      {({ houses, projects, users }) => (
        <>
          <OverviewStats houses={houses} projects={projects} users={users} />
          <HousesSummaryTable
            houses={houses}
            projects={projects}
            users={users}
          />
        </>
      )}
    </Async>
  );
}
