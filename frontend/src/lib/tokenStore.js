// Access token: memory only (gone on refresh).
// Refresh token: sessionStorage (gone when the tab closes).
const REFRESH_KEY = "fb.refresh";
let accessToken = null;

export function getAccessToken() {
  return accessToken;
}

export function getRefreshToken() {
  try {
    return sessionStorage.getItem(REFRESH_KEY);
  } catch {
    return null;
  }
}

export function saveTokens({ access, refresh }) {
  if (access) accessToken = access;
  if (refresh) {
    try {
      sessionStorage.setItem(REFRESH_KEY, refresh);
    } catch {
      // Storage blocked. The user will log in again after a refresh.
    }
  }
}

export function clearTokens() {
  accessToken = null;
  try {
    sessionStorage.removeItem(REFRESH_KEY);
  } catch {
    // Nothing to clear.
  }
}
