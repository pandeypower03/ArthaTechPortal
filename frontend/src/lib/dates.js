// Every date on screen is shown in Indian time.
const TIME_ZONE = "Asia/Kolkata";

const dateFormat = new Intl.DateTimeFormat("en-IN", {
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: TIME_ZONE,
});

const dateTimeFormat = new Intl.DateTimeFormat("en-IN", {
  day: "numeric",
  month: "short",
  hour: "numeric",
  minute: "2-digit",
  hour12: true,
  timeZone: TIME_ZONE,
});

export function formatDate(iso) {
  return dateFormat.format(new Date(iso));
}

export function formatDateTime(iso) {
  return dateTimeFormat.format(new Date(iso));
}
