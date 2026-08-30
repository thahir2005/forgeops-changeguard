
const API_BASE_URL = "http://localhost:8000";

async function postJson(path, payload) {

  const response = await fetch(

    `${API_BASE_URL}${path}`,

    {

      method: "POST",

      headers: {

        "Content-Type": "application/json",

      },

      body: JSON.stringify(payload),

    }

  );

  if (!response.ok) {

    let message = `API request failed: ${response.status}`;

    try {

      const error = await response.json();

      if (error.detail) {

        message = error.detail;

      }

    } catch {

      // Keep the default error message.

    }

    throw new Error(message);

  }

  return response.json();

}

export async function analyzeChange(payload) {

  return postJson(

    "/api/v1/changes/analyze",

    payload

  );

}

export async function analyzePullRequest(payload) {

  return postJson(

    "/api/v1/pull-requests/analyze",

    payload

  );

}
