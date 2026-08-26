import axios from 'axios'
import { SESSION_STORAGE_KEY } from '../context/session'

// In dev, Vite proxies /api -> http://127.0.0.1:8000 (see vite.config.js).
// In production, set VITE_API_BASE_URL to the deployed backend URL.
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const apiClient = axios.create({
  baseURL,
  headers: {
    Accept: 'application/json',
  },
})

function readStoredToken() {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)?.token ?? null
  } catch {
    return null
  }
}

// Attach the JWT bearer token (if a session is signed in) to every
// request - harmless for the endpoints that don't require auth,
// required for the protected ones (approvals, reimbursement).
apiClient.interceptors.request.use((config) => {
  const token = readStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginAttempt = error?.config?.url?.includes('/auth/login')

    // A 401 on anything other than the login form itself means the
    // stored token is missing/invalid/expired - clear the stale
    // session and send the user back to sign in, rather than
    // surfacing a confusing "Could not validate credentials" toast
    // on every subsequent request.
    if (error?.response?.status === 401 && !isLoginAttempt) {
      try {
        localStorage.removeItem(SESSION_STORAGE_KEY)
      } catch {
        // ignore
      }
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    const message =
      error?.response?.data?.detail ||
      error?.message ||
      'Something went wrong talking to the ExpenseIQ API.'

    return Promise.reject(new Error(message))
  },
)

export default apiClient
