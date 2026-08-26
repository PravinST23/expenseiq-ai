import { useEffect, useMemo, useState } from 'react'
import { SessionContext, SESSION_STORAGE_KEY } from './session'

function loadSession() {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function SessionProvider({ children }) {
  const [session, setSession] = useState(() => loadSession())

  useEffect(() => {
    if (session) {
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
    } else {
      localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  }, [session])

  const value = useMemo(
    () => ({
      session,
      isAuthenticated: Boolean(session),
      signIn: (payload) => setSession(payload),
      signOut: () => setSession(null),
    }),
    [session],
  )

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  )
}
