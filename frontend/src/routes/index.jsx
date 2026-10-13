import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "../components/layout/AppShell.jsx";
import { adminNav } from "../features/platform-admin/nav.js";
import LoginPage from "../pages/login/LoginPage.jsx";
import ComingSoonPage from "../pages/platform-admin/ComingSoonPage.jsx";
import OverviewPage from "../pages/platform-admin/OverviewPage.jsx";
import ProtectedRoute from "./ProtectedRoute.jsx";
import { isPlatformAdmin } from "./roleHome.js";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<ProtectedRoute allow={isPlatformAdmin} />}>
        <Route
          path="/admin"
          element={<AppShell roleLabel="Platform Admin" nav={adminNav} />}
        >
          <Route index element={<OverviewPage />} />
          <Route
            path="houses"
            element={<ComingSoonPage title="Production houses" />}
          />
          <Route path="users" element={<ComingSoonPage title="Users" />} />
          <Route
            path="audit-log"
            element={<ComingSoonPage title="Audit log" />}
          />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
