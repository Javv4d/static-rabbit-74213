import mockData from "./data/mockMrr.json";

const USE_MOCK = true;

export async function fetchMrrData() {
  if (USE_MOCK) {
    return mockData;
  }

  const response = await fetch("/api/mrr");
  if (!response.ok) {
    throw new Error("Failed to load MRR data");
  }
  return response.json();
}
