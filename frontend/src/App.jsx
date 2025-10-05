import { useEffect, useState } from 'react'
import './App.css'
import { health, uploadFile, listMaskings, getMasked, getOriginal } from './api'

function App() {
  const [serverOk, setServerOk] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [file, setFile] = useState(null)
  const [items, setItems] = useState([])
  const [selected, setSelected] = useState(null)
  const [masked, setMasked] = useState(null)

  useEffect(() => {
    health().then(() => setServerOk(true)).catch(() => setServerOk(false))
    refresh()
  }, [])

  async function refresh() {
    try {
      const data = await listMaskings()
      setItems(data)
    } catch (e) {
      console.error(e)
    }
  }

  async function onUpload(e) {
    e.preventDefault()
    if (!file) return
    setUploading(true)
    try {
      const res = await uploadFile(file, true)
      setSelected(res.masking_id)
      setMasked(res.masked)
      await refresh()
    } catch (e) {
      alert('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  async function selectItem(id) {
    setSelected(id)
    const data = await getMasked(id)
    setMasked(data?.masked_content ?? null)
  }

  async function revealOriginal() {
    if (!selected) return
    const data = await getOriginal(selected)
    alert('Original fetched (check console).')
    console.log('ORIGINAL', data)
  }

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <h2>Optiv Masking Demo</h2>
      <div style={{ marginBottom: 12 }}>Backend: {serverOk ? 'Online' : 'Offline'}</div>

      <form onSubmit={onUpload} style={{ marginBottom: 16 }}>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button type="submit" disabled={uploading || !file} style={{ marginLeft: 8 }}>
          {uploading ? 'Processing...' : 'Upload & Mask'}
        </button>
        <button type="button" disabled style={{ marginLeft: 8 }} title="Coming soon">
          Analyse
        </button>
      </form>

      <div style={{ display: 'flex', gap: 24 }}>
        <div style={{ width: 300 }}>
          <h3>My Maskings</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {items.map((it) => (
              <li key={it.masking_id}>
                <button onClick={() => selectItem(it.masking_id)} style={{ width: '100%', textAlign: 'left' }}>
                  {it.file_name}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div style={{ flex: 1 }}>
          <h3>Masked JSON</h3>
          <pre style={{ background: '#111', color: '#0f0', padding: 12, borderRadius: 6, minHeight: 300 }}>
{masked ? JSON.stringify(masked, null, 2) : 'Select an item or upload to view masked JSON'}
          </pre>
          <div>
            <button onClick={revealOriginal} disabled={!selected}>
              Reveal Original (auth required)
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
