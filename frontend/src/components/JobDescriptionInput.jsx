import styles from './JobDescriptionInput.module.css'

/**
 * Job description textarea - controlled component.
 *
 * @param {string} value - current job description text
 * @param {(value: string) => void} onChange
 */
function JobDescriptionInput({ value, onChange }) {
  return (
    <div className={styles.card}>
      <h2 className={styles.title}>2. Paste Job Description</h2>
      <textarea
        className={styles.textarea}
        placeholder="Paste the job description here..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={8}
      />
    </div>
  )
}

export default JobDescriptionInput
