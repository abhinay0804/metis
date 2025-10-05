import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://127.0.0.1:8001',
});

export async function health() {
  const { data } = await api.get('/health');
  return data;
}

export async function uploadFile(file, reversible = true) {
  const form = new FormData();
  form.append('file', file);
  form.append('reversible', String(reversible));
  const { data } = await api.post('/process', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function listMaskings() {
  const { data } = await api.get('/maskings');
  return data;
}

export async function getMasked(maskingId) {
  const { data } = await api.get(`/maskings/${maskingId}`);
  return data;
}

export async function getOriginal(maskingId) {
  const { data } = await api.get(`/maskings/${maskingId}/original`);
  return data;
}


