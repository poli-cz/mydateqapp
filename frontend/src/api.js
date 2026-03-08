const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function apiFetch(path, options = {}) {
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `API request failed: ${response.status}`;
    try {
      const data = await response.json();
      message = data?.detail
        ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail))
        : message;
    } catch {
      try {
        const text = await response.text();
        if (text) message = text;
      } catch {
        // ignore body parse failure
      }
    }
    throw new Error(message);
  }

  return response.json();
}

export async function getHealth() {
  return apiFetch("/api/health");
}

export async function analyzeProfile(payload) {
  return apiFetch("/api/analyze-profile", {
    method: "POST",
    body: payload instanceof FormData ? payload : JSON.stringify(payload),
  });
}

export async function joinWaitlist(payload) {
  return apiFetch("/api/waitlist", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export { API_BASE_URL };