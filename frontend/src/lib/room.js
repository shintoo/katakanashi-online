import { reactive } from 'vue'

// One live connection to a room. Messages are handled in order, and an event
// handler can return a promise (an animation) that holds back the next update.
export function connectRoom(code, token, { onEvent, onEnd }) {
  const live = reactive({ state: null, status: 'connecting', error: null })
  let socket = null
  let retry = 0
  let stopped = false
  let queue = Promise.resolve()

  function open() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    socket = new WebSocket(`${proto}://${location.host}/ws/${code}?token=${encodeURIComponent(token)}`)
    socket.onopen = () => {
      retry = 0
      live.status = 'open'
    }
    socket.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      queue = queue.then(() => handle(msg)).catch((err) => console.error(err))
    }
    socket.onclose = (e) => {
      if (stopped) return
      if (e.code === 4401) return finish('unknown')
      if (e.code === 4403) return finish('removed')
      if (e.code === 4404) return finish('closed')
      live.status = 'reconnecting'
      retry = Math.min(retry + 1, 6)
      setTimeout(() => !stopped && open(), 400 * 2 ** (retry - 1))
    }
  }

  async function handle(msg) {
    if (msg.type === 'state') live.state = msg.state
    else if (msg.type === 'event') await onEvent(msg, live.state)
    else if (msg.type === 'error') {
      live.error = { message: msg.message, at: Date.now() }
    } else if (msg.type === 'closed') finish('closed')
    else if (msg.type === 'removed') finish('removed')
  }

  function finish(reason) {
    if (stopped) return
    stopped = true
    socket?.close()
    onEnd(reason)
  }

  function send(type, data = {}) {
    if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type, ...data }))
  }

  function close() {
    stopped = true
    socket?.close()
  }

  open()
  return { live, send, close }
}
