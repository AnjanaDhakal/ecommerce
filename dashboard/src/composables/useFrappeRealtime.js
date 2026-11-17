import { io } from 'socket.io-client'

let socket
const listeners = new Map()

const getSocketUrl = () => {
  const baseUrl = import.meta.env.VITE_FRAPPE_URL || window.location.origin
  return baseUrl.replace(/\/$/, '')
}

const getSocketOptions = () => ({
  path: '/socket.io',
  transports: ['websocket', 'polling'],
  withCredentials: true,
})

const ensureSocket = () => {
  if (socket) {
    return socket
  }

  socket = io(getSocketUrl(), getSocketOptions())

  socket.on('connect_error', (error) => {
    console.warn('Frappe realtime connection failed:', error?.message || error)
  })

  return socket
}

export const initFrappeRealtime = () => ensureSocket()

export const onFrappeRealtime = (eventName, handler) => {
  const realtimeSocket = ensureSocket()

  if (!listeners.has(eventName)) {
    listeners.set(eventName, new Set())
    realtimeSocket.on(eventName, (payload) => {
      for (const callback of listeners.get(eventName) || []) {
        callback(payload)
      }
    })
  }

  listeners.get(eventName).add(handler)

  return () => {
    const eventListeners = listeners.get(eventName)
    if (!eventListeners) {
      return
    }

    eventListeners.delete(handler)
    if (eventListeners.size === 0) {
      listeners.delete(eventName)
      realtimeSocket.off(eventName)
    }
  }
}
