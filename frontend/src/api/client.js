// 后端 API 封装:文档列表 / 上传(带进度) / 流式问答(SSE)

const BASE = '/api'

export async function listDocuments() {
  const res = await fetch(`${BASE}/documents`)
  if (!res.ok) throw new Error(`获取文档列表失败 (${res.status})`)
  return res.json()
}

// 上传单个文件,onProgress(percent 0-100)。用 XHR 以拿到上传进度。
export function uploadDocument(file, onProgress) {
  return new Promise((resolve, reject) => {
    const form = new FormData()
    form.append('file', file)
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${BASE}/documents`)
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        let msg = `上传失败 (${xhr.status})`
        try {
          msg = JSON.parse(xhr.responseText).detail || msg
        } catch (_) {}
        reject(new Error(msg))
      }
    }
    xhr.onerror = () => reject(new Error('网络错误,上传失败'))
    xhr.send(form)
  })
}

// 流式问答。回调:onMeta({conversation_id}) / onToken(text) / onSources(list) /
// onError(msg) / onDone({conversation_id})
export async function chatStream(
  { question, conversationId },
  { onMeta, onToken, onSources, onError, onDone } = {},
) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, conversation_id: conversationId ?? null }),
  })
  if (!res.ok || !res.body) {
    let msg = `请求失败 (${res.status})`
    try {
      msg = (await res.json()).detail || msg
    } catch (_) {}
    onError && onError(msg)
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  // 解析一段 SSE 文本块:event: X\ndata: Y
  const dispatch = (raw) => {
    let event = 'message'
    let data = ''
    for (const line of raw.split('\n')) {
      if (line.startsWith('event:')) event = line.slice(6).trim()
      else if (line.startsWith('data:')) data += line.slice(5).trim()
    }
    if (!data) return
    let payload
    try {
      payload = JSON.parse(data)
    } catch (_) {
      return
    }
    if (event === 'meta') onMeta && onMeta(payload)
    else if (event === 'token') onToken && onToken(payload.text)
    else if (event === 'sources') onSources && onSources(payload)
    else if (event === 'error') onError && onError(payload.message)
    else if (event === 'done') onDone && onDone(payload)
  }

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const block = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      if (block.trim()) dispatch(block)
    }
  }
}
