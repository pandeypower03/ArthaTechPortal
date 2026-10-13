import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../features/auth/useAuth.js";

// Hiding a screen is only for looks. The backend still checks permissions on every call.
// allow: a function like isPlatformAdmin that says which users may enter.
export default function ProtectedRoute({ allow }) {
  const { user, loading } = useAuth();

  if (loading) return <p className="p-6 text-brand-soft">Checking session…</p>;
  if (!user || !allow(user)) return <Navigate to="/login" replace />;

  return <Outlet />;
}
