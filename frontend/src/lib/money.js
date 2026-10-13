// Money is always whole paise (an integer). Only this file turns it into text for the screen.

const rupeeFormat = new Intl.NumberFormat("en-IN");

const PAISE_IN_RUPEE = 100;
const RUPEES_IN_LAKH = 100_000;
const RUPEES_IN_CRORE = 10_000_000;

// 1234500 paise -> "₹12,345"
export function formatRupees(paise) {
  return "₹" + rupeeFormat.format(Math.round(paise / PAISE_IN_RUPEE));
}

// 1250000000 paise -> "₹1.25 Cr", 4500000 paise -> "₹45 L"
export function formatShort(paise) {
  const rupees = paise / PAISE_IN_RUPEE;
  if (rupees >= RUPEES_IN_CRORE) return `₹${trim(rupees / RUPEES_IN_CRORE)} Cr`;
  if (rupees >= RUPEES_IN_LAKH) return `₹${trim(rupees / RUPEES_IN_LAKH)} L`;
  return formatRupees(paise);
}

function trim(number) {
  return String(Number(number.toFixed(2)));
}
