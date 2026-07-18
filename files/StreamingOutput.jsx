import Loader from './Loader.jsx'
import styles from './StreamingOutput.module.css'

/**
 * Status indicator below the results cards.
 *
 * Product decision: if `error` is set, it takes over the whole box (the
 * calling component - App.jsx - is responsible for having already cleared
 * the result cards themselves; this component just surfaces the message).
 *
 * @param {boolean} isLoading
 * @param {string|null} error
 */
function StreamingOutput({ isLoading, error }) {
  if (error) {
    return (
      <div className={`${styles.wrapper} ${styles.wrapperError}`}>
        <p className={styles.errorText}>⚠ {error}</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.loadingRow}>
          <Loader />
          <span className={styles.loadingText}>Analyzing your resume...</span>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>
      <p className={styles.text}>Analysis output will stream here in real time.</p>
    </div>
  )
}

export default StreamingOutput
