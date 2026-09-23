import { useEffect, useMemo, useRef, useState } from 'react';

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function formatSeverity(value) {
  return value ? value.replace('_', ' ').toUpperCase() : 'NONE';
}

function severityClass(value) {
  const map = {
    none: 'severity-none',
    smoke_only: 'severity-smoke',
    small_fire: 'severity-small',
    active_wildfire: 'severity-active',
  };
  return map[value] || 'severity-none';
}

function App() {
  const [tab, setTab] = useState('image');
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [threshold, setThreshold] = useState(0.35);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const canvasRef = useRef(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  async function fetchHistory() {
    try {
      const response = await fetch(`${API}/api/history`);
      if (!response.ok) throw new Error('history request failed');
      const data = await response.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    }
  }

  function onFileChange(event) {
    const nextFile = event.target.files?.[0];
    if (!nextFile) return;
    setFile(nextFile);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(nextFile));
    setResult(null);
  }

  function drawDetections(image, detections) {
    const canvas = canvasRef.current;
    if (!canvas || !image) return;
    const ctx = canvas.getContext('2d');
    canvas.width = image.width;
    canvas.height = image.height;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

    detections.forEach((detection) => {
      const bbox = detection.bbox || [0, 0, 0, 0];
      const x = bbox[0] * image.width;
      const y = bbox[1] * image.height;
      const width = (bbox[2] - bbox[0]) * image.width;
      const height = (bbox[3] - bbox[1]) * image.height;
      ctx.strokeStyle = detection.class.toLowerCase() === 'fire' ? '#ff5a3d' : '#fbbf24';
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, width, height);
      ctx.fillStyle = '#0b1120';
      ctx.fillRect(x, Math.max(0, y - 28), 150, 22);
      ctx.fillStyle = '#fff';
      ctx.font = '12px sans-serif';
      ctx.fillText(`${detection.class} ${(detection.confidence * 100).toFixed(0)}%`, x + 8, Math.max(12, y - 12));
    });
  }

  async function submit() {
    if (!file) {
      setError('Choose an image or video file first.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const form = new FormData();
      form.append('file', file);
      const response = await fetch(`${API}/api/analyze?confidenceThreshold=${threshold}`, {
        method: 'POST',
        body: form,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Analysis failed');
      }

      setResult(data);
      if (file.type.startsWith('image/')) {
        const img = new Image();
        img.onload = () => drawDetections(img, data.detections || []);
        img.src = previewUrl;
      }
      fetchHistory();
    } catch (err) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  const summaryCards = useMemo(() => [
    { label: 'Status', value: result ? formatSeverity(result.severity) : 'READY' },
    { label: 'Confidence', value: result ? `${(result.detections?.[0]?.confidence || 0).toFixed(2)}` : '0.35' },
    { label: 'Detections', value: result ? `${result.detections?.length || 0}` : '0' },
    { label: 'History', value: `${history.length}` },
  ], [result, history]);

  return (
    <div className="forest-page">
      <header className="topbar">
        <div>
          <p className="eyebrow">Wildfire Intelligence</p>
          <h1>ForestGuard</h1>
        </div>
        <div className="top-actions">
          <span className="live-badge">YOLO26 wildfire detection</span>
        </div>
      </header>

      <div className="summary-grid">
        {summaryCards.map(({ label, value }) => (
          <div className="summary-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <div className="main-grid">
        <section className="panel uploader-panel">
          <div className="panel-header">
            <h2>Analyze media</h2>
            <div className="segmented">
              {['image', 'video'].map((value) => (
                <button key={value} className={tab === value ? 'active' : ''} onClick={() => setTab(value)}>
                  {value === 'image' ? 'Image' : 'Video'}
                </button>
              ))}
            </div>
          </div>

          <label className="upload-box">
            <input type="file" accept={tab === 'image' ? 'image/*' : 'video/*'} onChange={onFileChange} />
            <span>{file ? file.name : `Upload ${tab}`}</span>
          </label>

          <div className="slider-row">
            <label>Confidence threshold</label>
            <div className="slider-wrap">
              <input type="range" min="0.05" max="0.95" step="0.05" value={threshold} onChange={(e) => setThreshold(parseFloat(e.target.value))} />
              <strong>{threshold.toFixed(2)}</strong>
            </div>
          </div>

          <button className="primary-btn" onClick={submit} disabled={loading || !file}>
            {loading ? 'Analyzing...' : 'Run detection'}
          </button>

          {error && <div className="error-box">{error}</div>}
        </section>

        <section className="panel preview-panel">
          <div className="panel-header">
            <h2>Detection preview</h2>
          </div>
          <div className="preview-area">
            {previewUrl ? (
              <>
                <img src={previewUrl} alt="Selected media" style={{ display: file?.type?.startsWith('image/') ? 'block' : 'none' }} />
                <canvas ref={canvasRef} style={{ display: file?.type?.startsWith('image/') ? 'block' : 'none' }} />
                {file?.type?.startsWith('video/') && <div className="video-placeholder">Video preview will be processed on the backend.</div>}
              </>
            ) : (
              <div className="empty-state">Upload a local wildfire image or video to begin.</div>
            )}
          </div>
        </section>
      </div>

      <section className="panel result-panel">
        <div className="panel-header">
          <h2>Results</h2>
        </div>
        {result ? (
          <div className="result-box">
            <div className={`badge ${severityClass(result.severity)}`}>{formatSeverity(result.severity)}</div>
            <div className="result-grid">
              <div><span>File</span><strong>{result.filename}</strong></div>
              <div><span>Detections</span><strong>{result.detections?.length || 0}</strong></div>
              <div><span>Top confidence</span><strong>{Math.max(...(result.detections?.map(d => d.confidence) || [0])).toFixed(2)}</strong></div>
            </div>
            <div className="detection-list">
              {(result.detections || []).map((d, index) => (
                <div key={`${d.class}-${index}`} className="detection-item">
                  <span>{d.class}</span>
                  <strong>{(d.confidence * 100).toFixed(1)}%</strong>
                  <small>{JSON.stringify(d.bbox)}</small>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="empty-state">No analysis results yet.</div>
        )}
      </section>

      <section className="panel history-panel">
        <div className="panel-header">
          <h2>Detection history</h2>
        </div>
        <div className="history-list">
          {history.length ? history.map((entry, index) => (
            <div key={`${entry.filename}-${index}`} className="history-item">
              <div>
                <strong>{entry.filename}</strong>
                <small>{new Date(entry.timestamp).toLocaleString()}</small>
              </div>
              <div className={`badge ${severityClass(entry.severity)}`}>{formatSeverity(entry.severity)}</div>
              <span>{(entry.top_detection_confidence || 0).toFixed(2)}</span>
            </div>
          )) : <div className="empty-state">No previous detections recorded.</div>}
        </div>
      </section>
    </div>
  );
}

export default App;
