// The backend only tells us is_superuser for now. Project roles come with a later backend change.
export function isPlatformAdmin(user) {
  return user.is_superuser;
}

// Where a user lands after login. null means "no screens for this user yet".
export function roleHome(user) {
  return isPlatformAdmin(user) ? "/admin" : null;
}
