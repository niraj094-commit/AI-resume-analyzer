/**
 * API service layer.
 *
 * Every backend call the frontend makes goes through this file - no
 * scattered fetch() calls in components. This keeps the streaming/parsing
 * logic in one testable place.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

/**
 * Send a resume + job description to the backend and stream back the
 * analysis. Each complete NDJSON line (one JSON object) is passed to
 * `onChunk` as soon as it's fully received - e.g.
 *   { field: "ats_score", value: 78 }
 *   { field: "error", value: "..." }
 *
 * @param {File} file - the resume PDF
 * @param {string} jobDescription - pasted job description text
 * @param {(chunk: {field: string, value: any}) => void} onChunk - called
 *   once per complete JSON object as it streams in
 *
 * @throws if the request itself fails before streaming starts (e.g. a 400
 *   validation error from the backend, or a network failure). Errors that
 *   happen mid-stream (after the backend has already sent a 200) instead
 *   arrive as a normal chunk with field: "error" - see useStreamingAnalysis.
 */
export async function analyzeResume(file, jobDescription, onChunk) {
  const formData = new FormData()
  formData.append('resume', file)
  formData.append('job_description', jobDescription)

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    // Pre-stream failures (400 validation errors, etc.) arrive as a
    // normal JSON body, not NDJSON - surface the backend's detail message.
    let message = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (body?.detail) {
        message = typeof body.detail === 'string' ? body.detail : message
      }
    } catch {
      // Response body wasn't JSON - fall back to the generic message above.
    }
    throw new Error(message)
  }

  if (!response.body) {
    throw new Error('Streaming is not supported in this browser.')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    // NDJSON = one complete JSON object per line. Split on newlines, but
    // keep the last (possibly incomplete) piece in the buffer for the
    // next read - the server rarely flushes exactly on line boundaries.
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue
      onChunk(JSON.parse(trimmed))
    }
  }

  // Handle a final line that didn't end with a trailing newline.
  const trimmed = buffer.trim()
  if (trimmed) {
    onChunk(JSON.parse(trimmed))
  }
}

export { API_BASE_URL }
