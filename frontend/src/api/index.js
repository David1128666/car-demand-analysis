const BASE = "/api/v1";

async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(BASE + path, { ...options, headers });
  if (res.status === 401) {
    // Only remove token if not in the middle of login
    if (!path.startsWith("/auth/login") && !path.startsWith("/auth/register")) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
  }
  const json = await res.json();
  if (!res.ok) {
    let msg = json.data?.message || "Request failed";
    if (!msg && json.detail) {
      if (typeof json.detail === "string") msg = json.detail;
      else if (Array.isArray(json.detail)) msg = json.detail.map(d => d.msg).join("; ");
    }
    throw new Error(msg);
  }
  return json;
}

const api = {
  get: (path, params) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return request(path + qs);
  },
  post: (path, body) => request(path, { method: "POST", body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: (path, body) => request(path, { method: "DELETE", body: body ? JSON.stringify(body) : undefined }),
};

export default api;