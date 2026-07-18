import { useState } from 'react'
import ResumeUpload from './components/ResumeUpload.jsx'
import JobDescriptionInput from './components/JobDescriptionInput.jsx'
import AnalyzeButton from './components/AnalyzeButton.jsx'
import StreamingOutput from './components/StreamingOutput.jsx'
import ATSScoreCard from './components/ResultsPanel/ATSScoreCard.jsx'
import MatchPercentage from './components/ResultsPanel/MatchPercentage.jsx'
import MissingSkills from './components/ResultsPanel/MissingSkills.jsx'
import SuggestionsList from './components/ResultsPanel/SuggestionsList.jsx'
import { useStreamingAnalysis } from './hooks/useStreamingAnalysis.js'
import styles from './App.module.css'

/**
 * Root layout + orchestration.
 *
 * File and job-description state are lifted up here (rather than living
 * inside ResumeUpload/JobDescriptionInput) so AnalyzeButton can read both
 * when the user clicks "Analyze". The actual request/streaming logic lives
 * in useStreamingAnalysis - this component just wires props together.
 */
function App() {
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')

  const { isLoading, result, error, runAnalysis } = useStreamingAnalysis()

  const canAnalyze = file !== null && jobDescription.trim().length > 0 && !isLoading

  const handleAnalyzeClick = () => {
    if (!canAnalyze) return
    runAnalysis(file, jobDescription)
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>AI Resume Analyzer</h1>
        <p>Upload your resume, paste a job description, get instant AI feedback.</p>
      </header>

      <main className={styles.mainGrid}>
        <section className={styles.inputColumn}>
          <ResumeUpload file={file} onFileChange={setFile} />
          <JobDescriptionInput value={jobDescription} onChange={setJobDescription} />
          <AnalyzeButton onClick={handleAnalyzeClick} disabled={!canAnalyze} isLoading={isLoading} />
        </section>

        <section className={styles.resultsColumn}>
          <ATSScoreCard score={result.ats_score} />
          <MatchPercentage percentage={result.match_percentage} />
          <MissingSkills skills={result.missing_skills} />
          <SuggestionsList suggestions={result.suggestions} />
          <StreamingOutput isLoading={isLoading} error={error} />
        </section>
      </main>
    </div>
  )
}

export default App
