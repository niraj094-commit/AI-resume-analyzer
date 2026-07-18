import styles from './ResultsCards.module.css'

/**
 * @param {string[]|null} skills
 */
function MissingSkills({ skills }) {
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Missing Skills</h3>
      {!skills && <p className={styles.hint}>Run an analysis to see skills gaps</p>}
      {skills && skills.length === 0 && (
        <p className={styles.hint}>No major skill gaps found - nice work!</p>
      )}
      {skills && skills.length > 0 && (
        <ul className={styles.chipList}>
          {skills.map((skill) => (
            <li key={skill} className={styles.chip}>
              {skill}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default MissingSkills
