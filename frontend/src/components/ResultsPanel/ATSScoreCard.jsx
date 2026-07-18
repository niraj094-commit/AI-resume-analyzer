import styles from './ResultsCards.module.css'

/**
 * @param {number|null} score - 0-100, or null if not yet available
 */
function ATSScoreCard({ score }) {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>ATS Score</h3>
      <p className={styles.placeholder}>{score != null ? `${score} / 100` : '— / 100'}</p>
      {score == null && <p className={styles.hint}>Run an analysis to see your score</p>}
    </div>
  )
}

export default ATSScoreCard
