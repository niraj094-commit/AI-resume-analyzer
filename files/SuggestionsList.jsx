import styles from './ResultsCards.module.css'

/**
 * @param {string[]|null} suggestions
 */
function SuggestionsList({ suggestions }) {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Improvement Suggestions</h3>
      {!suggestions && <p className={styles.hint}>Run an analysis to see suggestions</p>}
      {suggestions && suggestions.length > 0 && (
        <ul className={styles.suggestionList}>
          {suggestions.map((suggestion) => (
            <li key={suggestion}>{suggestion}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default SuggestionsList
