import { ref } from 'vue'

const stored = Number(localStorage.getItem('liveUpdateCount') || 0)
const liveUpdateCount = ref(isNaN(stored) ? 0 : stored)
const storedOpenInit = Number(localStorage.getItem('liveOpenInitCount') || 0)
const liveOpenInitCount = ref(isNaN(storedOpenInit) ? 0 : storedOpenInit)

// allow direct import of the refs when needed
export { liveUpdateCount, liveOpenInitCount }

export const useLiveUpdateCount = () => {
  const setLiveUpdateCount = (val: number) => {
    const safeVal = Number(val) || 0
    liveUpdateCount.value = safeVal
    localStorage.setItem('liveUpdateCount', String(safeVal))
  }
  const setLiveOpenInitCount = (val: number) => {
    const safeVal = Number(val) || 0
    liveOpenInitCount.value = safeVal
    localStorage.setItem('liveOpenInitCount', String(safeVal))
  }
  return { liveUpdateCount, setLiveUpdateCount, liveOpenInitCount, setLiveOpenInitCount }
}
