export const PROJECT_TYPES = {
  movie: "Movie",
  ott: "OTT series",
  ad: "Ad film",
  other: "Other",
};

// Assumption: plan prices are placeholders, only to show earnings per house.
export const PLANS = {
  starter: "Starter",
  studio: "Studio",
  enterprise: "Enterprise",
};

export const ROLE_LABELS = {
  producer: "Producer",
  lineproducer: "Line Producer",
  pm: "Production Manager",
  teamhead: "Team Head",
  auditor: "Auditor",
  accountant: "Accountant",
  finance: "Finance",
};

export function toOptions(labels) {
  return Object.entries(labels);
}
