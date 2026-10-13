import { useCallback, useEffect, useMemo, useState } from "react";
import { getRefreshToken } from "../../lib/tokenStore.js";
import { AuthContext } from "./authContext.js";
import * as authApi from "./api.js";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // If a refresh token exists, we first check with the backend who the user is.
  const [loading, setLoading] = useState(() => Boolean(getRefreshToken()));

  useEffect(() => {
    if (!getRefreshToken()) return;
    let cancelled = false;
    authApi
      .fetchMe()
      .then((me) => !cancelled && setUser(me))
      .catch(() => {
        // Session ended or token is old. The user simply sees the login page.
      })
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback(async (identifier, password) => {
    const loggedInUser = await authApi.login(identifier, password);
    setUser(loggedInUser);
    return loggedInUser;
  }, []);

  const signOut = useCallback(async () => {
    setUser(null);
    await authApi.logout();
  }, []);

  const value = useMemo(
    () => ({ user, loading, signIn, signOut }),
    [user, loading, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
