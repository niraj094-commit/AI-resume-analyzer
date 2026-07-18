import { useState } from 'react'
import styles from './ResumeUpload.module.css'

/**
 * PDF upload card - controlled component.
 *
 * The selected File object lives in App.jsx (lifted up) so AnalyzeButton
 * can access it when the user clicks "Analyze". This component only owns
 * transient UI state (drag-over highlight).
 *
 * @param {File|null} file - currently selected resume file
 * @param {(file: File) => void} onFileChange - called when a new file is chosen
 */
function ResumeUpload({ file, onFileChange }) {
  const [isDragOver, setIsDragOver] = useState(false)

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0]
    if (selected) onFileChange(selected)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragOver(false)
    const dropped = event.dataTransfer.files?.[0]
    if (dropped) onFileChange(dropped)
  }

  return (
    <div className={styles.card}>
      <h2 className={styles.title}>1. Upload Resume (PDF)</h2>

      <label
        className={`${styles.dropzone} ${isDragOver ? styles.dropzoneActive : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragOver(true)
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className={styles.hiddenInput}
        />
        <span>{file ? file.name : 'Click or drag a PDF resume here'}</span>
      </label>
    </div>
  )
}

export default ResumeUpload
