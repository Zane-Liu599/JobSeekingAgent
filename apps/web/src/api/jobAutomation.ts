export type JobLead = {
  id: number | null;
  title: string;
  company: string;
  location: string;
  employment_type: string;
  salary: string;
  platform: string;
  job_url: string;
  official_apply_url: string;
  description: string;
  status: string;
  match_score: number | null;
  created_at: string;
};

export type JobPayload = {
  title: string;
  company: string;
  location: string;
  employment_type: string;
  salary: string;
  platform: string;
  job_url: string;
  description: string;
};

export type SearchPayload = {
  keywords: string;
  location: string;
  platform?: string;
};

export type SearchResponse = {
  message: string;
  saved_count: number;
  blocked: boolean;
  refreshed: boolean;
  refresh_message: string;
  jobs: JobLead[];
};

export type CoverLetterResponse = {
  job_id: number;
  path: string;
  text: string;
  provider: string;
  model: string;
  used_resume: boolean;
  used_template: boolean;
  error: string;
};

export function applyUrlForJob(job: JobLead): string {
  return job.official_apply_url || job.job_url;
}

const apiBase = "/api/ai";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {})
    },
    ...options
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || response.statusText);
  }

  return response.json() as Promise<T>;
}

export async function fetchJobs(): Promise<JobLead[]> {
  const data = await request<{ jobs: JobLead[] }>("/jobs");
  return data.jobs;
}

export async function exportJobsExcel(): Promise<Blob> {
  const response = await fetch(`${apiBase}/jobs/export`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || response.statusText);
  }
  return response.blob();
}

export async function createJob(payload: JobPayload): Promise<JobLead> {
  return request<JobLead>("/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function searchJobs(payload: SearchPayload) {
  return request<SearchResponse>("/jobs/search", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function updateJobsStatus(jobIds: number[], status: string) {
  return request<{ updated: number }>("/jobs/status", {
    method: "PATCH",
    body: JSON.stringify({ job_ids: jobIds, status })
  });
}

export async function deleteJobs(jobIds: number[]) {
  return request<{ deleted: number }>("/jobs", {
    method: "DELETE",
    body: JSON.stringify({ job_ids: jobIds })
  });
}

export async function generateCoverLetter(jobId: number) {
  return request<CoverLetterResponse>("/cover-letters/generate", {
    method: "POST",
    body: JSON.stringify({ job_id: jobId })
  });
}

export async function fetchApplicationPlan(jobId: number) {
  return request<{ steps: string[] }>(`/applications/plan/${jobId}`);
}
