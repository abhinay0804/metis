export type MaskingListItem = {
  masking_id: string;
  file_name: string;
  file_type: string;
  created_at?: string;
  reversible?: boolean;
};

const BASE_URL = 'http://localhost:8001';

export async function apiHealth(): Promise<any> {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
}

function authHeaders(token?: string) {
  // For local development, don't send auth headers to allow dev bypass
  if (import.meta.env.DEV) {
    return {};
  }
  const t = token || localStorage.getItem('idToken') || '';
  return t ? { 'Authorization': `Bearer ${t}` } : {};
}

export async function apiProcess(file: File, reversible: boolean, token?: string): Promise<any> {
  console.log('API Process called with:', { fileName: file.name, reversible, token });
  console.log('BASE_URL:', BASE_URL);
  
  const form = new FormData();
  form.append('file', file);
  form.append('reversible', String(reversible));
  
  const headers = authHeaders(token);
  console.log('Headers:', headers);
  
  try {
    const res = await fetch(`${BASE_URL}/process`, {
      method: 'POST',
      body: form,
      headers: headers,
    });
    console.log('Response status:', res.status);
    console.log('Response ok:', res.ok);
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('Response error:', errorText);
      throw new Error(errorText);
    }
    
    const result = await res.json();
    console.log('Response data:', result);
    return result;
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}

export async function apiListMaskings(token?: string): Promise<MaskingListItem[]> {
  console.log('API ListMaskings called');
  const url = `${BASE_URL}/maskings?_=${Date.now()}`; // cache buster
  const res = await fetch(url, { headers: { ...authHeaders(token) }, cache: 'no-store' });
  console.log('ListMaskings response status:', res.status);
  if (!res.ok) {
    const errorText = await res.text();
    console.error('ListMaskings error:', errorText);
    throw new Error(errorText);
  }
  const data = await res.json();
  console.log('ListMaskings data:', data);
  return data;
}

export async function apiGetMasked(maskingId: string, token?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/maskings/${maskingId}`, { headers: { ...authHeaders(token) } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiListAnalyses(token?: string): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/analyses`, { headers: { ...authHeaders(token) }, cache: 'no-store' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiGetAnalysis(analysisId: string, token?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/analyses/${analysisId}`, { headers: { ...authHeaders(token) }, cache: 'no-store' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiAnalyze(file: File, token?: string): Promise<any> {
  console.log('API Analyze called with:', { fileName: file.name, fileType: file.type, token });
  console.log('BASE_URL:', BASE_URL);
  
  const form = new FormData();
  form.append('file', file);
  
  const headers = authHeaders(token);
  console.log('Headers:', headers);
  
  try {
    const res = await fetch(`${BASE_URL}/analyze`, { 
      method: 'POST', 
      body: form, 
      headers: headers 
    });
    console.log('Analyze response status:', res.status);
    console.log('Analyze response ok:', res.ok);
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('Analyze response error:', errorText);
      throw new Error(errorText);
    }
    
    const result = await res.json();
    console.log('Analyze response data:', result);
    return result;
  } catch (error) {
    console.error('Analyze fetch error:', error);
    throw error;
  }
}

