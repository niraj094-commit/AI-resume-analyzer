import styles from './ResultsCards.module.css'

/**
 * @param {number|null} percentage - 0-100, or null if not yet available
 */
function MatchPercentage({ percentage }) {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Match Percentage</h3>
      <p className={styles.placeholder}>{percentage != null ? `${percentage}%` : '—%'}</p>
      {percentage == null && (
        <p className={styles.hint}>How well your resume matches the job description</p>
      )}
    </div>
  )
}

export default MatchPercentage
