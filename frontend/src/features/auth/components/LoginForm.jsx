import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../../components/ui/Button.jsx";
import Modal from "../../../components/ui/Modal.jsx";
import { Field, Input } from "../../../components/ui/Field.jsx";
import { roleHome } from "../../../routes/roleHome.js";
import { useAuth } from "../useAuth.js";

export default function LoginForm() {
  const { signIn, signOut } = useAuth();
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showForgot, setShowForgot] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const user = await signIn(identifier, password);
      const home = roleHome(user);
      if (!home) {
        await signOut();
        setError(
          "Only the Platform Admin can sign in for now. Other roles come in later phases.",
        );
        setBusy(false);
        return;
      }
      navigate(home, { replace: true });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <section className="flex w-full max-w-140 flex-col justify-center gap-5.5 px-5 py-7 md:px-11 md:py-12">
      <div>
        <h2 className="text-2xl font-semibold">Sign in</h2>
        <p className="mt-1 text-ink-2">
          Use your email or username and your password.
        </p>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <Field label="Email or username">
          <Input
            type="text"
            autoComplete="username"
            placeholder="you@company.in"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
          />
        </Field>
        <Field label="Password">
          <Input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </Field>

        {error && (
          <p
            role="alert"
            className="mb-2.5 rounded-lg bg-bad-wash px-3 py-2 text-bad"
          >
            {error}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-3">
          <Button
            type="submit"
            variant="primary"
            disabled={busy || !identifier || !password}
          >
            {busy ? "Signing in…" : "Sign in"}
          </Button>
          <Button variant="ghost" onClick={() => setShowForgot(true)}>
            Forgot password?
          </Button>
        </div>
      </form>

      {showForgot && (
        <Modal title="Forgot password" onClose={() => setShowForgot(false)}>
          <p>
            Password reset by email is built as a hook and switched off for now.
          </p>
          <p className="mt-3 rounded-lg bg-panel px-3 py-2.5 text-[13.5px] text-ink-2">
            Ask the Platform Admin to reset it. They will set a temporary
            password and unlock your account if it was locked.
          </p>
          <div className="mt-3 flex justify-end">
            <Button variant="primary" onClick={() => setShowForgot(false)}>
              OK
            </Button>
          </div>
        </Modal>
      )}
    </section>
  );
}
