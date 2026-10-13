import { Navigate } from "react-router-dom";
import LoginArt from "../../features/auth/components/LoginArt.jsx";
import LoginForm from "../../features/auth/components/LoginForm.jsx";
import { useAuth } from "../../features/auth/useAuth.js";
import { roleHome } from "../../routes/roleHome.js";

export default function LoginPage() {
  const { user, loading } = useAuth();

  if (loading) return <p className="p-6 text-brand-soft">Checking session…</p>;
  if (user && roleHome(user)) return <Navigate to={roleHome(user)} replace />;

  return (
    <div className="grid min-h-full md:grid-cols-[1.05fr_1fr]">
      <LoginArt />
      <LoginForm />
    </div>
  );
}
