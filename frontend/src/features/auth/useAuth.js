import { useContext } from "react";
import { AuthContext } from "./authContext.js";

// const { user, loading, signIn, signOut } = useAuth()
export function useAuth() {
  return useContext(AuthContext);
}
