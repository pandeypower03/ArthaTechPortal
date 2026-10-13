import PageHead from "../../components/ui/PageHead.jsx";
import PlatformOverview from "../../features/platform-admin/components/PlatformOverview.jsx";

export default function OverviewPage() {
  return (
    <>
      <PageHead
        title="Platform overview"
        text="Every production house, project and user on the platform. Money data inside a house stays closed unless you open logged support access."
      />
      <PlatformOverview />
    </>
  );
}
