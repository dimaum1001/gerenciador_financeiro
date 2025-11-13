const NOTIFICATION_PREFS_KEY = 'notification_preferences'

export const defaultNotificationPreferences = {
  email_transacoes: true,
  email_orcamentos: true,
  email_vencimentos: true,
  push_transacoes: false,
  push_orcamentos: true,
  push_vencimentos: true,
}

export function loadNotificationPreferences() {
  if (typeof window === 'undefined') {
    return { ...defaultNotificationPreferences }
  }

  try {
    const stored = window.localStorage.getItem(NOTIFICATION_PREFS_KEY)
    if (!stored) {
      return { ...defaultNotificationPreferences }
    }
    const parsed = JSON.parse(stored)
    return { ...defaultNotificationPreferences, ...parsed }
  } catch {
    return { ...defaultNotificationPreferences }
  }
}

export function saveNotificationPreferences(preferences) {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(
      NOTIFICATION_PREFS_KEY,
      JSON.stringify({ ...defaultNotificationPreferences, ...preferences })
    )
    window.dispatchEvent(new CustomEvent('notification-preferences-updated'))
  } catch {
    // ignore storage errors (private mode, etc)
  }
}

export function subscribeNotificationPreferences(callback) {
  if (typeof window === 'undefined') {
    return () => {}
  }
  const handler = () => {
    callback(loadNotificationPreferences())
  }
  window.addEventListener('notification-preferences-updated', handler)
  return () => window.removeEventListener('notification-preferences-updated', handler)
}

