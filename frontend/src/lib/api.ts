export type MaskingListItem = {
  masking_id: string;
  file_name: string;
  file_type: string;
  status: string;
  created_at?: string;
  reversible?: boolean;
};

const BASE_URL = '/api';

export async function apiHealth(): Promise<any> {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
}

function authHeaders(token?: string) {
  const t = token || localStorage.getItem('idToken') || '';
  return t ? { 'Authorization': `Bearer ${t}` } : {};
}

export async function apiLogin(email: string, password: string) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiRegister(email: string, password: string, fullName: string) {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiGetMe() {
  const res = await fetch(`${BASE_URL}/auth/me`, {
    headers: authHeaders()
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const apiHistory = async () => {
  const res = await fetch(`${BASE_URL}/history`, { headers: authHeaders() });
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
};

export const apiStats = async () => {
  const res = await fetch(`${BASE_URL}/dashboard-data?_=${Date.now()}`, { headers: authHeaders(), cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
};

export async function apiUpdateMe(data: any) {
  const res = await fetch(`${BASE_URL}/auth/me`, {
    method: 'PUT',
    headers: {
      ...authHeaders(),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiUpdatePhoto(photoBase64: string) {
  const res = await fetch(`${BASE_URL}/auth/photo`, {
    method: 'POST',
    headers: {
      ...authHeaders(),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ photo_base64: photoBase64 })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiProcess(file: File, reversible: boolean, token?: string, onProgress?: (p: number) => void): Promise<any> {
  
  const form = new FormData();
  form.append('file', file);
  form.append('reversible', String(reversible));
  
  const headers = authHeaders(token);
  
  try {
    const res = await fetch(`${BASE_URL}/process`, {
      method: 'POST',
      body: form,
      headers: headers,
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('Response error:', errorText);
      throw new Error(errorText);
    }
    
    const result = await res.json();
    
    // Polling logic for async masking
    if (result.status === 'pending' && result.job_id) {
      let simProgress = 10;
      if (onProgress) onProgress(simProgress);
      
      while (true) {
        await new Promise(r => setTimeout(r, 1000));
        simProgress = Math.min(simProgress + 15, 90);
        if (onProgress) onProgress(simProgress);
        
        const pollRes = await fetch(`${BASE_URL}/history/${result.job_id}`, { headers });
        if (pollRes.ok) {
          const pollData = await pollRes.json();
          const pStatus = (pollData.status || '').toLowerCase();
          if (pStatus === 'completed') {
            if (onProgress) onProgress(100);
            return {
              job_id: pollData.job_id,
              masked: pollData.masked_content,
              detection_summary: pollData.detection_summary,
              processing_time_ms: pollData.processing_time_ms
            };
          } else if (pStatus === 'failed') {
            throw new Error(pollData.error_message || 'Processing failed');
          }
        } else {
          if (pollRes.status === 401 || pollRes.status === 403) {
            throw new Error("Session expired or unauthorized. Please log in again.");
          }
          throw new Error(`Polling failed with status ${pollRes.status}`);
        }
      }
    }
    
    // Fallback if not pending
    return {
      masked: result.result?.masked_content || result.masked || result.result,
      job_id: result.job_id
    };
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}

export async function apiListMaskings(token?: string): Promise<any[]> {
  const url = `${BASE_URL}/history?_=${Date.now()}`; // cache buster
  const res = await fetch(url, { headers: { ...authHeaders(token) }, cache: 'no-store' });
  if (!res.ok) {
    const errorText = await res.text();
    console.error('ListMaskings error:', errorText);
    throw new Error(errorText);
  }
  const data = await res.json();
  // Map backend history schema to frontend masking list schema
  return data.map((job: any) => ({
    masking_id: job.job_id,
    file_name: job.file_name,
    file_type: job.file_type,
    job_type: job.job_type || 'masking',
    status: job.status,
    created_at: job.created_at,
    reversible: job.is_reversible === true
  }));
}

export async function apiGetMasked(maskingId: string, token?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/history/${maskingId}`, { headers: { ...authHeaders(token) } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiUnmask(maskingId: string, token?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/unmask/${maskingId}`, { 
    method: 'POST',
    headers: { ...authHeaders(token) } 
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiListAnalyses(token?: string): Promise<any[]> {
  const url = `${BASE_URL}/history?_=${Date.now()}`;
  const res = await fetch(url, { headers: { ...authHeaders(token) }, cache: 'no-store' });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data
    .filter((job: any) => job.job_type === 'analysis')
    .map((job: any) => ({
      analysis_id: job.job_id,
      file_name: job.file_name,
      file_type: job.file_type,
      status: job.status,
      created_at: job.created_at,
    }));
}

export async function apiGetAnalysis(analysisId: string, token?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/history/${analysisId}`, { headers: { ...authHeaders(token) }, cache: 'no-store' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiAnalyze(file: File, token?: string): Promise<any> {
  
  const form = new FormData();
  form.append('file', file);
  
  const headers = authHeaders(token) as Record<string, string>;
  const geminiKey = localStorage.getItem('geminiApiKey');
  if (geminiKey) {
    headers['X-Gemini-API-Key'] = geminiKey;
  }
  
  try {
    const res = await fetch(`${BASE_URL}/analyze`, { 
      method: 'POST', 
      body: form, 
      headers: headers 
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('Analyze response error:', errorText);
      throw new Error(errorText);
    }
    
    const result = await res.json();
    return result;
  } catch (error) {
    console.error('Analyze fetch error:', error);
    throw error;
  }
}

