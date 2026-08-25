const API_BASE_URL = "http://localhost:8000";


export async function analyzeChange(payload) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/changes/analyze`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status}`
    );
  }

  return response.json();
}
