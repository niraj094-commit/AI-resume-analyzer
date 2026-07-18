import { useCallback, useState } from 'react'
import { analyzeResume } from '../services/api'

const EMPTY_RESULT = {
  ats_score: null,
  match_percentage: null,
  missing_skills: null,
  suggestions: null,
}

/**
 * Drives the full analyze flow: calls the streaming API, accumulates
 * results field-by-field as they arrive, and exposes simple state for
 * components to render.
 *
 * Product decision: if Gemini's response includes a field: "error" chunk
 * (a failure that happened AFTER the backend already started streaming a
 * 200 response), we clear any partial results already shown and display
 * only the error - rather than showing a partially-complete analysis that
 * might be misleading.
 */
export function useStreamingAnalysis() {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(EMPTY_RESULT)
  const [error, setError] = useState(null)

  const runAnalysis = useCallback(async (file, jobDescription) => {
    setIsLoading(true)
    setError(null)
    setResult(EMPTY_RESULT)

    try {
      await analyzeResume(file, jobDescription, (chunk) => {
        if (chunk.field === 'error') {
          // Mid-stream failure - clear everything, surface only the error.
          setResult(EMPTY_RESULT)
          setError(chunk.value)
          return
        }
        setResult((prev) => ({ ...prev, [chunk.field]: chunk.value }))
      })
    } catch (err) {
      // Pre-stream failure (network error, 400 validation, etc.)
      setResult(EMPTY_RESULT)
      setError(err.message || 'Something went wrong while analyzing your resume.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  return { isLoading, result, error, runAnalysis }
}
