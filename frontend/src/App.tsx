
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import {
  Activity, AudioLines, BookOpen, ChartNoAxesCombined, Check,
  ChevronRight, CircleAlert, FlaskConical, FolderClock,
  LayoutDashboard, LoaderCircle, Mic, RefreshCw, Search,
  Upload, Volume2, Waves, X,
} from "lucide-react";
import {
  CartesianGrid, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from "recharts";
import {
  compareReports, getReport, getReports, getSummary,
  getTrends, transcribeAudio,
} from "./services/api";
import type {
  AnalyticsSummary, ReportSummary, TrendPoint,
} from "./services/api";
import { vocabularyDomains } from "./types";
import "./style.css";

type Page =
  | "Dashboard"
  | "Dictation Studio"
  | "Vocabulary Lab"
  | "Analytics"
  | "Experiments";

const navigation = [
  { name: "Dashboard" as Page, icon: LayoutDashboard },
  { name: "Dictation Studio" as Page, icon: Mic },
  { name: "Vocabulary Lab" as Page, icon: BookOpen },
  { name: "Analytics" as Page, icon: ChartNoAxesCombined },
  { name: "Experiments" as Page, icon: FlaskConical },
];

const emptySummary: AnalyticsSummary = {
  total_reports: 0,
  average_baseline_wer: null,
  average_enhanced_wer: null,
  average_baseline_f1: null,
  average_enhanced_f1: null,
  reports_with_wer: 0,
  reports_with_f1: 0,
};

function percent(value: number | null | undefined) {
  return value == null ? "—" : `${(value * 100).toFixed(2)}%`;
}

function dateLabel(value: string) {
  return new Date(value).toLocaleString();
}

function App() {
  const [page, setPage] = useState<Page>("Dashboard");
  const [summary, setSummary] = useState<AnalyticsSummary>(emptySummary);
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  const refresh = async () => {
    setLoading(true);
    setApiError("");
    try {
      const [s, r, t] = await Promise.all([
        getSummary(), getReports(), getTrends(),
      ]);
      setSummary(s);
      setReports(r);
      setTrends(t);
    } catch (error: any) {
      setApiError(
        error?.response?.data?.detail ||
        "Could not connect to the VOXERA API. Check that FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Waves size={23} /></div>
          <div>
            <div className="brand-name">VOXERA</div>
            <div className="brand-subtitle">VOICE INTELLIGENCE</div>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <nav>
          {navigation.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={`nav-item ${page === name ? "active" : ""}`}
              onClick={() => setPage(name)}
            >
              <Icon size={18} />
              <span>{name}</span>
              {page === name && <ChevronRight size={15} className="nav-arrow" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="provider-card">
            <span className="status-dot" />
            <div>
              <strong>API connection</strong>
              <small>{apiError ? "Connection issue" : "VOXERA backend"}</small>
            </div>
          </div>
          <div className="sidebar-foot">INDEPENDENT · OPEN SOURCE</div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <div className="topbar-kicker">VOICE INTELLIGENCE PLATFORM</div>
            <h1>{page}</h1>
          </div>
          <div className="topbar-actions">
            <span className={`connection-pill ${apiError ? "offline" : ""}`}>
              <span className="status-dot" />
              {apiError ? "API unavailable" : "System connected"}
            </span>
            <button className="icon-button" onClick={() => void refresh()} title="Refresh data">
              <RefreshCw size={17} />
            </button>
          </div>
        </header>

        {apiError && (
          <div className="alert error-alert">
            <CircleAlert size={18} />
            <span>{apiError}</span>
            <button onClick={() => void refresh()}>Retry</button>
          </div>
        )}

        {page === "Dashboard" && (
          <Dashboard
            summary={summary}
            reports={reports}
            trends={trends}
            loading={loading}
            onNavigate={setPage}
          />
        )}
        {page === "Dictation Studio" && <DictationStudio />}
        {page === "Vocabulary Lab" && <VocabularyLab />}
        {page === "Analytics" && (
          <Analytics summary={summary} trends={trends} reports={reports} loading={loading} />
        )}
        {page === "Experiments" && <Experiments reports={reports} onRefresh={refresh} />}
      </main>
    </div>
  );
}

function PageIntro({
  eyebrow, title, description, action,
}: {
  eyebrow: string; title: string; description: string; action?: ReactNode;
}) {
  return (
    <div className="page-intro">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      {action}
    </div>
  );
}

function MetricCard({
  label, value, detail, icon: Icon,
}: {
  label: string; value: string; detail: string; icon: any;
}) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <Icon size={18} />
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-detail">{detail}</div>
    </article>
  );
}

function Dashboard({
  summary, reports, trends, loading, onNavigate,
}: {
  summary: AnalyticsSummary;
  reports: ReportSummary[];
  trends: TrendPoint[];
  loading: boolean;
  onNavigate: (page: Page) => void;
}) {
  const chartData = trends.map((item) => ({
    ...item,
    label: new Date(item.created_at).toLocaleTimeString([], {
      hour: "2-digit", minute: "2-digit",
    }),
  }));

  return (
    <div className="content">
      <PageIntro
        eyebrow="OVERVIEW / 01"
        title="Your voice. Your intelligence."
        description="Monitor transcription quality, technical vocabulary and experiment performance."
        action={<span className="live-tag"><span className="status-dot" /> LIVE DATA</span>}
      />

      <div className="metric-grid">
        <MetricCard label="TOTAL EXPERIMENTS" value={loading ? "…" : String(summary.total_reports)} detail="Saved benchmark reports" icon={FlaskConical} />
        <MetricCard label="BASELINE WER" value={percent(summary.average_baseline_wer)} detail="Average word error rate" icon={Activity} />
        <MetricCard label="ENHANCED WER" value={percent(summary.average_enhanced_wer)} detail="Vocabulary-enhanced pipeline" icon={Waves} />
        <MetricCard label="ENHANCED TECHNICAL F1" value={percent(summary.average_enhanced_f1)} detail="Technical-term evaluation" icon={ChartNoAxesCombined} />
      </div>

      <div className="dashboard-grid">
        <section className="panel chart-panel">
          <div className="panel-heading">
            <div>
              <div className="eyebrow">PERFORMANCE</div>
              <h3>Recognition trends</h3>
            </div>
            <span className="subtle-tag">WER · lower is better</span>
          </div>
          {chartData.length ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid stroke="#24364d" strokeDasharray="3 3" />
                  <XAxis dataKey="label" stroke="#7187a4" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#7187a4" tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                  <Tooltip
                    contentStyle={{ background: "#101d30", border: "1px solid #2a4260", borderRadius: 10 }}
                    formatter={(value) => percent(typeof value === "number" ? value : null)}
                  />
                  <Line type="monotone" dataKey="baseline_wer" name="Baseline WER" stroke="#f5a65b" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="enhanced_wer" name="Enhanced WER" stroke="#75bdff" strokeWidth={2.5} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="empty-state"><ChartNoAxesCombined size={28} /><p>No trend data available yet.</p></div>
          )}
        </section>

        <section className="panel quick-panel">
          <div className="eyebrow">QUICK ACTIONS</div>
          <h3>Continue building</h3>
          <button className="quick-action" onClick={() => onNavigate("Dictation Studio")}>
            <span className="quick-icon"><Mic size={18} /></span>
            <span><strong>Start dictation</strong><small>Transcribe an audio recording</small></span>
            <ChevronRight size={17} />
          </button>
          <button className="quick-action" onClick={() => onNavigate("Vocabulary Lab")}>
            <span className="quick-icon"><BookOpen size={18} /></span>
            <span><strong>Explore vocabulary</strong><small>Browse engineering terminology</small></span>
            <ChevronRight size={17} />
          </button>
          <button className="quick-action" onClick={() => onNavigate("Experiments")}>
            <span className="quick-icon"><FolderClock size={18} /></span>
            <span><strong>View experiments</strong><small>Inspect saved benchmark reports</small></span>
            <ChevronRight size={17} />
          </button>
        </section>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <div><div className="eyebrow">LATEST ACTIVITY</div><h3>Recent experiments</h3></div>
          <button className="text-button" onClick={() => onNavigate("Experiments")}>View all <ChevronRight size={15} /></button>
        </div>
        <ReportTable reports={reports.slice(0, 5)} />
      </section>
    </div>
  );
}

function DictationStudio() {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("auto");
  const [domains, setDomains] = useState(["digital_design", "verification"]);
  const [vocabularyEnabled, setVocabularyEnabled] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<any>(null);
  const [recording, setRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [recordedUrl, setRecordedUrl] = useState("");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const toggleDomain = (id: string) => {
    setDomains((current) =>
      current.includes(id) ? current.filter((x) => x !== id) : [...current, id]
    );
  };

  const startRecording = async () => {
    setError("");
    setResult(null);

    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("Microphone recording is not supported in this browser. Try the latest Chrome or Edge.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];

      const mimeCandidates = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/mp4",
      ];
      const mimeType = mimeCandidates.find((type) => MediaRecorder.isTypeSupported(type));
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onerror = () => {
        setError("An error occurred while recording. Please try again.");
        setRecording(false);
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });

        if (blob.size > 0) {
          const extension = blob.type.includes("mp4") ? "m4a" : "webm";
          const recordedFile = new File(
            [blob],
            `voxera-recording-${Date.now()}.${extension}`,
            { type: blob.type }
          );

          setFile(recordedFile);
          setRecordedUrl(URL.createObjectURL(blob));
        } else {
          setError("The recording was empty. Please record again.");
        }

        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        setRecording(false);
      };

      recorder.start();
      setRecordingSeconds(0);
      setRecording(true);
    } catch (err: any) {
      const message =
        err?.name === "NotAllowedError"
          ? "Microphone permission was denied. Allow microphone access in your browser and try again."
          : err?.name === "NotFoundError"
          ? "No microphone was found. Connect a microphone and try again."
          : "Could not start microphone recording. Check your browser permissions.";
      setError(message);
    }
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
  };

  useEffect(() => {
    if (!recording) return;
    const timer = window.setInterval(() => {
      setRecordingSeconds((seconds) => seconds + 1);
    }, 1000);
    return () => window.clearInterval(timer);
  }, [recording]);

  useEffect(() => {
    return () => {
      const recorder = mediaRecorderRef.current;
      if (recorder && recorder.state !== "inactive") recorder.stop();
      streamRef.current?.getTracks().forEach((track) => track.stop());
      if (recordedUrl) URL.revokeObjectURL(recordedUrl);
    };
  }, [recordedUrl]);

  const submit = async () => {
    if (!file) {
      setError("Choose an audio file or record audio before starting transcription.");
      return;
    }
    if (vocabularyEnabled && domains.length === 0) {
      setError("Select at least one vocabulary domain, or disable vocabulary.");
      return;
    }
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const response = await transcribeAudio(file, language, domains, vocabularyEnabled);
      setResult(response);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Transcription failed. Check the backend logs.");
    } finally {
      setBusy(false);
    }
  };

  const formatDuration = (seconds: number) =>
    `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;

  return (
    <div className="content">
      <PageIntro
        eyebrow="SPEECH / 02"
        title="Dictation Studio"
        description="Convert spoken engineering requirements into structured text with optional technical vocabulary."
      />

      <div className="studio-grid">
        <section className="panel studio-controls">
          <div className="panel-heading">
            <div><div className="eyebrow">INPUT CONFIGURATION</div><h3>Audio source</h3></div>
            <AudioLines size={21} />
          </div>

          <div className="recording-panel">
            <div className="recording-heading">
              <div>
                <div className="field-label">LIVE MICROPHONE</div>
                <small>{recording ? "Recording in progress" : "Record directly from your microphone"}</small>
              </div>
              <span className={`recording-timer ${recording ? "recording-active" : ""}`}>
                {recording && <span className="recording-dot" />}
                {formatDuration(recordingSeconds)}
              </span>
            </div>
            <button
              className={`record-button ${recording ? "record-button-stop" : ""}`}
              onClick={() => recording ? stopRecording() : void startRecording()}
              disabled={busy}
            >
              {recording ? <><span className="record-square" /> Stop recording</> : <><Mic size={17} /> Start microphone recording</>}
            </button>
            {recordedUrl && !recording && (
              <div className="recorded-preview">
                <span className="field-label">RECORDED AUDIO PREVIEW</span>
                <audio controls src={recordedUrl} />
              </div>
            )}
          </div>

          <label className="field-label">OR UPLOAD AN AUDIO FILE</label>
          <label className="upload-zone">
            <Upload size={25} />
            <strong>{file ? file.name : "Choose an audio file"}</strong>
            <span>{file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "WAV · MP3 · M4A · AAC · OGG · FLAC · WEBM"}</span>
            <input
              type="file"
              accept=".wav,.mp3,.m4a,.aac,.ogg,.flac,.webm,audio/*"
              onChange={(e) => {
                const selectedFile = e.target.files?.[0] || null;
                setFile(selectedFile);
                if (recordedUrl) URL.revokeObjectURL(recordedUrl);
                setRecordedUrl("");
                setError("");
                setResult(null);
              }}
            />
          </label>

          <label className="field-label" htmlFor="language">LANGUAGE</label>
          <select id="language" className="select-control" value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="auto">Auto detect</option>
            <option value="en-IN">English (India)</option>
            <option value="hi-IN">Hindi</option>
            <option value="te-IN">Telugu</option>
            <option value="ta-IN">Tamil</option>
            <option value="kn-IN">Kannada</option>
            <option value="ml-IN">Malayalam</option>
            <option value="bn-IN">Bengali</option>
            <option value="mr-IN">Marathi</option>
            <option value="gu-IN">Gujarati</option>
            <option value="pa-IN">Punjabi</option>
          </select>

          <div className="toggle-row">
            <div><strong>Engineering vocabulary</strong><small>Apply selected technical terms</small></div>
            <button
              className={`toggle ${vocabularyEnabled ? "on" : ""}`}
              role="switch"
              aria-checked={vocabularyEnabled}
              onClick={() => setVocabularyEnabled((v) => !v)}
            ><span /></button>
          </div>

          {vocabularyEnabled && (
            <div className="domain-select">
              <label className="field-label">VOCABULARY DOMAINS</label>
              {vocabularyDomains.map((domain) => (
                <label className="check-row" key={domain.id}>
                  <input type="checkbox" checked={domains.includes(domain.id)} onChange={() => toggleDomain(domain.id)} />
                  <span>{domain.label}</span>
                  <small>{domain.terms.length} terms</small>
                </label>
              ))}
            </div>
          )}

          {error && <div className="alert error-alert"><CircleAlert size={16} />{String(error)}</div>}

          <button className="primary-button full-button" onClick={() => void submit()} disabled={busy || recording}>
            {busy ? <><LoaderCircle className="spin" size={17} /> Transcribing…</> : <><Mic size={17} /> Transcribe audio</>}
          </button>
          <p className="helper-text">Record with your microphone or upload audio. VOXERA sends the audio to its backend and configured speech provider.</p>
        </section>

        <section className="panel result-panel">
          <div className="panel-heading">
            <div><div className="eyebrow">OUTPUT</div><h3>Transcription result</h3></div>
            {result && <span className="success-tag"><Check size={13} /> COMPLETE</span>}
          </div>
          {!result ? (
            <div className="result-placeholder">
              <div className="placeholder-icon"><Volume2 size={28} /></div>
              <h3>Your transcript will appear here</h3>
              <p>Record or upload audio and start dictation to see the cleaned text, raw transcript and provider metadata.</p>
            </div>
          ) : (
            <div className="transcript-results">
              <div className="result-block">
                <div className="result-label">CLEANED TEXT <button onClick={() => void navigator.clipboard.writeText(result.result.text || "")}>Copy</button></div>
                <p>{result.result.text || "No cleaned text returned."}</p>
              </div>
              <div className="result-block">
                <div className="result-label">RAW TRANSCRIPT <button onClick={() => void navigator.clipboard.writeText(result.result.transcript || "")}>Copy</button></div>
                <p>{result.result.transcript || "No raw transcript returned."}</p>
              </div>
              <div className="metadata-grid">
                <div><small>PROVIDER</small><strong>{result.provider}</strong></div>
                <div><small>VOCABULARY</small><strong>{result.metadata.vocabulary_enabled ? "Enabled" : "Disabled"}</strong></div>
                <div><small>TERMS SENT</small><strong>{result.metadata.vocabulary_terms_used}</strong></div>
                <div><small>DEGRADED</small><strong>{String(result.result.degraded ?? "Unknown")}</strong></div>
              </div>
              <div className="result-block">
                <div className="result-label">USAGE & CORRECTIONS</div>
                <pre>{JSON.stringify({ usage: result.result.usage, corrections: result.result.corrections }, null, 2)}</pre>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function VocabularyLab() {
  const [query, setQuery] = useState("");
  const [activeDomain, setActiveDomain] = useState("all");

  const terms = useMemo(() => vocabularyDomains.flatMap((domain) =>
    domain.terms.map((term) => ({ term, domain: domain.label, domainId: domain.id }))
  ), []);

  const filtered = terms.filter((item) =>
    (activeDomain === "all" || item.domainId === activeDomain) &&
    `${item.term} ${item.domain}`.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="content">
      <PageIntro
        eyebrow="KNOWLEDGE / 03"
        title="Engineering Vocabulary"
        description="Explore the technical vocabulary catalogue used to configure enhanced dictation."
      />
      <section className="panel">
        <div className="vocab-toolbar">
          <div className="search-box"><Search size={17} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search FIFO, MOSFET, SVA…" /></div>
          <span className="subtle-tag">{filtered.length} TERMS</span>
        </div>
        <div className="filter-row">
          <button className={activeDomain === "all" ? "filter-chip selected" : "filter-chip"} onClick={() => setActiveDomain("all")}>All domains</button>
          {vocabularyDomains.map((d) => (
            <button key={d.id} className={activeDomain === d.id ? "filter-chip selected" : "filter-chip"} onClick={() => setActiveDomain(d.id)}>{d.label}</button>
          ))}
        </div>
        <div className="term-grid">
          {filtered.map((item) => (
            <article className="term-card" key={`${item.domainId}-${item.term}`}>
              <strong>{item.term}</strong>
              <span>{item.domain}</span>
            </article>
          ))}
          {!filtered.length && <div className="empty-state">No matching terms found.</div>}
        </div>
      </section>
      <p className="helper-text">This view reflects the vocabulary terms currently declared in the frontend catalogue. The backend remains the source used for transcription requests.</p>
    </div>
  );
}

function Analytics({
  summary, trends, reports, loading,
}: {
  summary: AnalyticsSummary; trends: TrendPoint[]; reports: ReportSummary[]; loading: boolean;
}) {
  const data = trends.map((item) => ({
    ...item,
    label: new Date(item.created_at).toLocaleDateString(),
  }));

  return (
    <div className="content">
      <PageIntro
        eyebrow="EVALUATION / 04"
        title="Analytics"
        description="Review aggregate transcription quality and the history of saved evaluation results."
      />
      <div className="metric-grid">
        <MetricCard label="BASELINE WER" value={percent(summary.average_baseline_wer)} detail="Average word error rate" icon={Activity} />
        <MetricCard label="ENHANCED WER" value={percent(summary.average_enhanced_wer)} detail="Average word error rate" icon={Waves} />
        <MetricCard label="BASELINE TECHNICAL F1" value={percent(summary.average_baseline_f1)} detail="Technical-term matching" icon={BookOpen} />
        <MetricCard label="ENHANCED TECHNICAL F1" value={percent(summary.average_enhanced_f1)} detail="Technical-term matching" icon={ChartNoAxesCombined} />
      </div>
      <section className="panel">
        <div className="panel-heading"><div><div className="eyebrow">WORD ERROR RATE</div><h3>Baseline vs enhanced</h3></div><span className="subtle-tag">{trends.length} DATA POINTS</span></div>
        <div className="large-chart">
          {data.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid stroke="#24364d" strokeDasharray="3 3" />
                <XAxis dataKey="label" stroke="#7187a4" tick={{ fontSize: 11 }} />
                <YAxis stroke="#7187a4" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip contentStyle={{ background: "#101d30", border: "1px solid #2a4260", borderRadius: 10 }} formatter={(value) => percent(typeof value === "number" ? value : null)} />
                <Line type="monotone" dataKey="baseline_wer" name="Baseline WER" stroke="#f5a65b" strokeWidth={2.5} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="enhanced_wer" name="Enhanced WER" stroke="#75bdff" strokeWidth={2.5} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : <div className="empty-state">{loading ? "Loading analytics…" : "No trend data yet."}</div>}
        </div>
      </section>
      <section className="panel">
        <div className="panel-heading"><div><div className="eyebrow">REPORT REGISTER</div><h3>Evaluation history</h3></div></div>
        <ReportTable reports={reports} />
      </section>
      <p className="helper-text">Metrics are computed from saved reports. Synthetic or manually supplied benchmark data should not be interpreted as real-world provider performance.</p>
    </div>
  );
}

function ReportTable({ reports }: { reports: ReportSummary[] }) {
  if (!reports.length) return <div className="empty-state">No experiment reports have been saved yet.</div>;

  return (
    <div className="table-scroll">
      <table>
        <thead><tr><th>EXPERIMENT</th><th>DATE</th><th>BASELINE WER</th><th>ENHANCED WER</th><th>BASELINE F1</th><th>ENHANCED F1</th></tr></thead>
        <tbody>
          {reports.map((report) => (
            <tr key={report.report_id}>
              <td><strong>{report.experiment_name}</strong><small className="table-id">{report.report_id}</small></td>
              <td>{dateLabel(report.created_at)}</td>
              <td>{percent(report.baseline_wer)}</td>
              <td className="blue-value">{percent(report.enhanced_wer)}</td>
              <td>{percent(report.baseline_f1)}</td>
              <td className="blue-value">{percent(report.enhanced_f1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Experiments({
  reports, onRefresh,
}: {
  reports: ReportSummary[]; onRefresh: () => Promise<void>;
}) {
  const [selected, setSelected] = useState<string[]>([]);
  const [detail, setDetail] = useState<any>(null);
  const [comparison, setComparison] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const openReport = async (id: string) => {
    setBusy(true);
    setError("");
    setComparison(null);
    try {
      setDetail(await getReport(id));
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not load report.");
    } finally {
      setBusy(false);
    }
  };

  const toggleSelected = (id: string) => {
    setSelected((current) => {
      if (current.includes(id)) return current.filter((x) => x !== id);
      if (current.length >= 20) return current;
      return [...current, id];
    });
  };

  const runComparison = async () => {
    if (selected.length < 2) {
      setError("Select at least two reports to compare.");
      return;
    }
    setBusy(true);
    setError("");
    setDetail(null);
    try {
      setComparison(await compareReports(selected));
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Comparison failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="content">
      <PageIntro
        eyebrow="RESEARCH / 05"
        title="Experiment Manager"
        description="Inspect saved benchmark reports and compare transcription experiments."
        action={<button className="secondary-button" onClick={() => void onRefresh()}><RefreshCw size={15} /> Refresh</button>}
      />
      {error && <div className="alert error-alert"><CircleAlert size={16} />{error}</div>}
      <section className="panel">
        <div className="panel-heading">
          <div><div className="eyebrow">SAVED EXPERIMENTS</div><h3>Report library</h3></div>
          <span className="subtle-tag">{reports.length} REPORTS</span>
        </div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>SELECT</th><th>EXPERIMENT</th><th>CREATED</th><th>ENHANCED WER</th><th>ENHANCED F1</th><th>DETAIL</th></tr></thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report.report_id}>
                  <td><input type="checkbox" checked={selected.includes(report.report_id)} onChange={() => toggleSelected(report.report_id)} /></td>
                  <td><strong>{report.experiment_name}</strong><small className="table-id">{report.report_id}</small></td>
                  <td>{dateLabel(report.created_at)}</td>
                  <td className="blue-value">{percent(report.enhanced_wer)}</td>
                  <td className="blue-value">{percent(report.enhanced_f1)}</td>
                  <td><button className="text-button" onClick={() => void openReport(report.report_id)}>Open <ChevronRight size={14} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {!reports.length && <div className="empty-state">No reports available.</div>}
        </div>
        <div className="compare-bar">
          <span>{selected.length} selected</span>
          <button className="primary-button" disabled={busy || selected.length < 2} onClick={() => void runComparison()}>
            {busy ? <LoaderCircle className="spin" size={16} /> : <ChartNoAxesCombined size={16} />}
            Compare selected
          </button>
        </div>
      </section>

      {busy && <div className="panel loading-panel"><LoaderCircle className="spin" /> Loading report…</div>}

      {detail && (
        <section className="panel detail-panel">
          <div className="panel-heading"><div><div className="eyebrow">REPORT DETAIL</div><h3>{detail.experiment_name}</h3></div><button className="icon-button" onClick={() => setDetail(null)}><X size={17} /></button></div>
          <p className="helper-text">{detail.report_id} · {dateLabel(detail.created_at)}</p>
          <div className="detail-grid">
            {["baseline", "enhanced"].map((variant) => (
              <div className="detail-card" key={variant}>
                <h4>{variant.toUpperCase()}</h4>
                <div className="detail-metric"><span>WER</span><strong>{percent(detail.benchmark?.[variant]?.wer?.wer)}</strong></div>
                <div className="detail-metric"><span>Technical F1</span><strong>{percent(detail.benchmark?.[variant]?.technical_metrics?.f1_score)}</strong></div>
                <div className="detail-metric"><span>Latency</span><strong>{detail.benchmark?.[variant]?.latency_seconds ?? "—"} s</strong></div>
                <p className="transcript-preview">{detail.benchmark?.[variant]?.hypothesis || "No transcript stored."}</p>
              </div>
            ))}
          </div>
          <pre className="json-view">{JSON.stringify(detail.benchmark?.comparison || {}, null, 2)}</pre>
        </section>
      )}

      {comparison && (
        <section className="panel detail-panel">
          <div className="panel-heading"><div><div className="eyebrow">MULTI-REPORT ANALYSIS</div><h3>Comparison result</h3></div><button className="icon-button" onClick={() => setComparison(null)}><X size={17} /></button></div>
          <p className="helper-text">{comparison.total} reports returned</p>
          {comparison.reports?.map((report: any) => (
            <div className="comparison-item" key={report.report_id}>
              <strong>{report.experiment_name}</strong>
              <small>{report.report_id}</small>
              <div className="comparison-stats">
                <span>Baseline WER: {percent(report.benchmark?.baseline?.wer?.wer)}</span>
                <span>Enhanced WER: {percent(report.benchmark?.enhanced?.wer?.wer)}</span>
                <span>Baseline F1: {percent(report.benchmark?.baseline?.technical_metrics?.f1_score)}</span>
                <span>Enhanced F1: {percent(report.benchmark?.enhanced?.technical_metrics?.f1_score)}</span>
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

export default App;
