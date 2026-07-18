/**
 * AnalysisContext.
 *
 * STUB — implemented in Step 5 (only if prop-drilling becomes unwieldy).
 *
 * Given the component tree is fairly shallow (App -> ResultsPanel cards),
 * we may end up NOT needing this and just passing props/using the
 * useStreamingAnalysis hook directly in App.jsx. Keeping the file here as a
 * placeholder so the decision is made deliberately in Step 5, not by
 * default.
 */

import { createContext, useContext } from 'react'

const AnalysisContext = createContext(null)

export function useAnalysisContext() {
  return useContext(AnalysisContext)
}

export default AnalysisContext
