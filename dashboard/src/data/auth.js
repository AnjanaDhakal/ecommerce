export function frappeOrigin() {
  if (window.location.port === '8080') {
    return `${window.location.protocol}//${window.location.hostname}:8000`
  }
  return window.location.origin
}

export function loginUrl(returnPath = '/website') {
  const dashboardUrl = new URL(`/ecommerce${returnPath}`, window.location.origin)
  return `${frappeOrigin()}/login?redirect-to=${encodeURIComponent(dashboardUrl.href)}`
}

export function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  const user = cookies.get('user_id')
  return user && user !== 'Guest' ? user : null
}
