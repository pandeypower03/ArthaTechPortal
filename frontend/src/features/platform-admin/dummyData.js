// Made-up data so the screens can be shown. Money is whole paise.
// Deleted when the backend has houses, projects and users.

export const houses = [
  {
    id: "h-sunrise",
    name: "Sunrise Pictures",
    city: "Mumbai",
    plan: "studio",
    monthlyFeePaise: 2499900,
    status: "active",
    createdAt: "2026-06-12T09:30:00+05:30",
    lastActivity: {
      at: "2026-10-13T18:05:00+05:30",
      action: "Day sheet approved",
    },
  },
  {
    id: "h-moon",
    name: "Moonlight Studios",
    city: "Mumbai",
    plan: "starter",
    monthlyFeePaise: 999900,
    status: "active",
    createdAt: "2026-08-03T11:00:00+05:30",
    lastActivity: {
      at: "2026-10-12T14:20:00+05:30",
      action: "Expense submitted",
    },
  },
  {
    id: "h-lotus",
    name: "Lotus Films",
    city: "Hyderabad",
    plan: "enterprise",
    monthlyFeePaise: 5999900,
    status: "suspended",
    createdAt: "2026-04-21T16:45:00+05:30",
    lastActivity: {
      at: "2026-09-02T10:10:00+05:30",
      action: "Payment batch approved",
    },
  },
];

export const projects = [
  { id: "p-king3", houseId: "h-sunrise", name: "King 3", type: "movie" },
  {
    id: "p-dhoop",
    houseId: "h-sunrise",
    name: "Dhoop (Season 1)",
    type: "ott",
  },
  { id: "p-glow", houseId: "h-moon", name: "Glow Soap Ad", type: "ad" },
  { id: "p-ranna", houseId: "h-lotus", name: "Ranna", type: "movie" },
];

export const users = [
  { id: 1, houseId: "h-sunrise", locked: false },
  { id: 2, houseId: "h-sunrise", locked: false },
  { id: 3, houseId: "h-sunrise", locked: false },
  { id: 4, houseId: "h-sunrise", locked: true },
  { id: 5, houseId: "h-sunrise", locked: false },
  { id: 6, houseId: "h-moon", locked: false },
  { id: 7, houseId: "h-moon", locked: false },
  { id: 8, houseId: "h-lotus", locked: false },
];
