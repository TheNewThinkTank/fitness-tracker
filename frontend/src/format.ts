export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T12:00:00`));
}

export function formatSplit(value: string | null): string {
  if (!value) return "Unspecified";
  return value.replace(/_/g, " ");
}