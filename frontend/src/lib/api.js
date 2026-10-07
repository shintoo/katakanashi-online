async function call(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || 'Something went wrong. Try again? (or ask Sean)')
  return data
}

export const createRoom = (name, icon) => call('POST', '/api/rooms', { name, icon })
export const joinRoom = (code, name, icon) => call('POST', `/api/rooms/${code}/players`, { name, icon })
export const roomInfo = (code) => call('GET', `/api/rooms/${code}`)

const key = (code) => `katakanashi:seat:${code.toUpperCase()}`

function read(k) {
  try {
    return JSON.parse(localStorage.getItem(k))
  } catch {
    return null
  }
}

function write(k, v) {
  try {
    if (v === null) localStorage.removeItem(k)
    else localStorage.setItem(k, JSON.stringify(v))
  } catch {
    // Private windows can block storage. The game still works, just without rejoining.
  }
}

export const getSeat = (code) => read(key(code))
export const saveSeat = (code, seat) => write(key(code), seat)
export const forgetSeat = (code) => write(key(code), null)
export const getProfile = () => read('katakanashi:profile')
export const saveProfile = (p) => write('katakanashi:profile', p)
export const seenHowTo = () => read('katakanashi:howto') === true
export const markHowTo = () => write('katakanashi:howto', true)
