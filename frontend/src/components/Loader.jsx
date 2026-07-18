import styles from './Loader.module.css'

/**
 * Small reusable spinner.
 *
 * @param {boolean} light - use light/white styling for dark backgrounds
 *   (e.g. inside the blue AnalyzeButton). Defaults to false (dark-on-light
 *   styling, for use on white/light card backgrounds like StreamingOutput).
 */
function Loader({ light = false }) {
  return (
    <div
      className={`${styles.spinner} ${light ? styles.spinnerLight : ''}`}
      aria-label="Loading"
      role="status"
    />
  )
}

export default Loader
