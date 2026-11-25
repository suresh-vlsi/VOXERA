
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

export interface DictationResponse {
  provider: string;
  result: {
    text: string | null;
    transcript: string | null;
    degraded: boolean | null;
    corrections: unknown[];
    usage: Record<string, unknown> | null;
  };
  metadata: {
    language_code: string;
    vocabulary_enabled: boolean;
    vocabulary_domains: string[];
    vocabulary_terms_used: number;
    audio_filename: string;
    audio_size_bytes: number;
  };
}

export interface ReportSummary {
  report_id: string;
  experiment_name: string;
  created_at: string;
  baseline_wer: number | null;
  enhanced_wer: number | null;
  baseline_f1: number | null;
  enhanced_f1: number | null;
}

export interface AnalyticsSummary {
  total_reports: number;
  average_baseline_wer: number | null;
  average_enhanced_wer: number | null;
  average_baseline_f1: number | null;
  average_enhanced_f1: number | null;
  reports_with_wer: number;
  reports_with_f1: number;
}

export interface TrendPoint {
  report_id: string;
  created_at: string;
  baseline_wer: number | null;
  enhanced_wer: number | null;
  baseline_f1: number | null;
  enhanced_f1: number | null;
}

export const getSummary = async () => {
  const { data } = await api.get("/analytics/summary");
  return data.summary as AnalyticsSummary;
};

export const getReports = async () => {
  const { data } = await api.get("/analytics/reports");
  return data.reports as ReportSummary[];
};

export const getTrends = async () => {
  const { data } = await api.get("/analytics/trends");
  return data.trends as TrendPoint[];
};

export const getReport = async (id: string) => {
  const { data } = await api.get(`/analytics/reports/${encodeURIComponent(id)}`);
  return data.report;
};

export const compareReports = async (ids: string[]) => {
  const { data } = await api.get("/analytics/compare", {
    params: { report_ids: ids.join(",") },
  });
  return data;
};

export const transcribeAudio = async (
  file: File,
  languageCode: string,
  domains: string[],
  vocabularyEnabled: boolean
) => {
  const form = new FormData();
  form.append("file", file);
  form.append("language_code", languageCode);
  form.append("vocabulary_domains", domains.join(","));
  form.append("vocabulary_enabled", String(vocabularyEnabled));

  const { data } = await api.post<DictationResponse>("/dictate", form);
  return data;
};
