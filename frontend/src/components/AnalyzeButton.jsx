import Loader from './Loader.jsx'
import styles from './AnalyzeButton.module.css'

/**
 * Primary call-to-action button.
 *
 * @param {() => void} onClick
 * @param {boolean} disabled - true when inputs are incomplete or a request is in flight
 * @param {boolean} isLoading - true while streaming is in progress
 */
function AnalyzeButton({ onClick, disabled, isLoading }) {
  return (
    <button className={styles.button} onClick={onClick} disabled={disabled}>
      {isLoading ? <Loader light /> : 'Analyze Resume'}
    </button>
  )
}

export default AnalyzeButton
