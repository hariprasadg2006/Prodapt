import { useRef, useState } from "react";

const ACCEPTED = [".pdf", ".docx", ".txt"];

function isAcceptedFile(file) {
  const name = file.name.toLowerCase();
  return ACCEPTED.some((ext) => name.endsWith(ext));
}

export default function FileUpload({ onUpload, loading }) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);
  const [rejected, setRejected] = useState([]);

  function pickFiles(fileList) {
    const files = Array.from(fileList);
    const accepted = files.filter(isAcceptedFile);
    const bad = files.filter((f) => !isAcceptedFile(f));
    setRejected(bad.map((f) => f.name));
    if (accepted.length) onUpload(accepted);
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragActive(false);
    if (loading) return;
    pickFiles(e.dataTransfer.files);
  }

  return (
    <div>
      <div
        className={`upload-zone${dragActive ? " upload-zone--active" : ""}${
          loading ? " upload-zone--loading" : ""
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          if (!loading) setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => !loading && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-disabled={loading}
      >
        <span className="upload-zone__icon" aria-hidden="true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 16V4m0 0L7 9m5-5l5 5"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M4 16v2.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V16"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
        <p className="upload-zone__title">
          {loading ? "Uploading…" : "Upload Research Files"}
        </p>
        <p className="upload-zone__hint">Drag &amp; drop .PDF, .DOCX, or .TXT</p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED.join(",")}
          className="upload-zone__input"
          onChange={(e) => {
            if (e.target.files?.length) pickFiles(e.target.files);
            e.target.value = "";
          }}
          disabled={loading}
        />
      </div>
      {rejected.length > 0 && (
        <p className="upload-zone__rejected" role="alert">
          Skipped unsupported file{rejected.length > 1 ? "s" : ""}: {rejected.join(", ")}
        </p>
      )}
    </div>
  );
}
