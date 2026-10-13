import { api } from "../../lib/apiClient.js";
import {
  clearTokens,
  getRefreshToken,
  saveTokens,
} from "../../lib/tokenStore.js";

// Backend answer: { access, refresh, user }
export async function login(identifier, password) {
  const data = await api("/accounts/login/", {
    method: "POST",
    auth: false,
    body: { identifier, password },
  });
  saveTokens(data);
  return data.user;
}

// "Who am I?" Works after a page refresh too: apiClient gets a new access token by itself.
export function fetchMe() {
  return api("/accounts/me/");
}

export async function logout() {
  const refresh = getRefreshToken();
  // Clear first, so the user is signed out on screen even if the server call fails.
  clearTokens();
  if (!refresh) return;
  try {
    await api("/accounts/logout/", {
      method: "POST",
      auth: false,
      body: { refresh },
    });
  } catch {
    // The token was already invalid. Nothing more to do.
  }
}
