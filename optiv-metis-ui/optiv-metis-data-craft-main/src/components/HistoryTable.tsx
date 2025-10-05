import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Search, Eye, Download, Filter, Calendar, Shield, BarChart3, FileText } from "lucide-react";
import { apiGetMasked, apiListMaskings, apiListAnalyses, apiGetAnalysis, MaskingListItem } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface HistoryTableProps {
  filter?: 'mask' | 'analysis';
  refreshTrigger?: number;
}

const HistoryTable = ({ filter, refreshTrigger }: HistoryTableProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [historyData, setHistoryData] = useState<any[]>([]);
  const { toast } = useToast();

  const loadHistory = async () => {
    try {
      const [maskItems, analysisItems] = await Promise.all([
        apiListMaskings(),
        apiListAnalyses().catch((err) => {
          console.warn('Analyses fetch failed (continuing with maskings only):', err);
          return [] as any[];
        }),
      ]);

      const masks = (maskItems as MaskingListItem[]).map((it) => ({
        id: it.masking_id,
        fileName: it.file_name,
        type: 'mask' as const,
        status: 'completed',
        createdAt: it.created_at ? new Date(it.created_at).getTime() : 0,
        date: it.created_at ? new Date(it.created_at).toISOString().slice(0, 10) : '',
        time: it.created_at ? new Date(it.created_at).toLocaleTimeString() : '',
        reversible: it.reversible ?? false,
      }));

      const analyses = (analysisItems as any[]).map((it: any) => {
        const id = it?.analysis_id || it?.id || it?.uuid || '';
        const fileName = it?.file_name || it?.filename || it?.name || 'Unknown';
        const created = it?.created_at || it?.createdAt || it?.timestamp || it?.date || '';
        const createdMs = created ? new Date(created).getTime() : 0;
        const status = it?.status || 'completed';
        return {
          id,
          fileName,
          type: 'analysis' as const,
          status,
          createdAt: createdMs,
          date: created ? new Date(created).toISOString().slice(0, 10) : '',
          time: created ? new Date(created).toLocaleTimeString() : '',
          reversible: false,
        };
      });

      const merged = [...masks, ...analyses].sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0));
      setHistoryData(merged);
    } catch (e) {
      console.error('Error loading history:', e);
      setHistoryData([]);
    }
  };

  useEffect(() => {
    loadHistory();
    const t = setTimeout(() => { loadHistory(); }, 800);
    const onFocus = () => { loadHistory(); };
    window.addEventListener('focus', onFocus);
    return () => { clearTimeout(t); window.removeEventListener('focus', onFocus); };
  }, [refreshTrigger]);

  const filteredData = historyData
    .filter((item) => !filter || item.type === filter)
    .filter((item) => item.fileName.toLowerCase().includes(searchTerm.toLowerCase()));

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-success">Completed</Badge>;
      case 'processing':
        return <Badge variant="secondary">Processing</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getTypeBadge = (type: string, reversible?: boolean) => (
    type === 'mask' ? (
      <Badge variant="secondary" className="bg-data-mask/10 text-data-mask border-data-mask/20">
        <Shield className="h-3 w-3 mr-1" />
        {reversible ? 'Reversible Masking' : 'Masking'}
      </Badge>
    ) : (
      <Badge variant="secondary" className="bg-data-analysis/10 text-data-analysis border-data-analysis/20">
        <BarChart3 className="h-3 w-3 mr-1" />
        Analysis
      </Badge>
    )
  );

  const downloadJson = (filename: string, data: any) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename.endsWith('.json') ? filename : `${filename}.json`;
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  };

  const MaskedJson = ({ maskingId, fileName }: { maskingId: string; fileName: string }) => {
    const [data, setData] = useState<any | null>(null);
    // Reversible/original features removed

    useEffect(() => {
      (async () => {
        try { setData(await apiGetMasked(maskingId)); } catch { setData({ error: 'Failed to load' }); }
      })();
    }, [maskingId]);

    const formatDataForDisplay = (d: any) => {
      if (!d) return d;
      const formatted = { ...d };
      if (formatted.masked_content) {
        const masked = { ...formatted.masked_content } as any;
        const hide = (val: any) => typeof val === 'string' && val.length > 0 ? `[base64 hidden] length=${val.length}` : val;
        if (typeof masked.base64_data === 'string') masked.base64_data = hide(masked.base64_data);
        if (typeof masked.redacted_image_base64 === 'string') masked.redacted_image_base64 = hide(masked.redacted_image_base64);
        formatted.masked_content = masked;
      }
      return formatted;
    };

    const sanitizeBase64 = (obj: any): any => {
      if (obj === null || obj === undefined) return obj;
      if (typeof obj !== 'object') return obj;
      if (Array.isArray(obj)) return obj.map(sanitizeBase64);
      const out: any = {};
      for (const k of Object.keys(obj)) {
        const v: any = (obj as any)[k];
        if ((k === 'base64_data' || k === 'redacted_image_base64') && typeof v === 'string') {
          out[k] = `[base64 hidden] length=${v.length}`;
        } else {
          out[k] = sanitizeBase64(v);
        }
      }
      return out;
    };

    const downloadBase64File = (name: string, base64: string, mime: string) => {
      const url = `data:${mime};base64,${base64}`;
      const a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    };

    // Helper to stop dialog from closing on internal button clicks
    const stop = (fn: () => void) => (e: React.MouseEvent) => { e.preventDefault(); e.stopPropagation(); fn(); };

    return (
      <div>
<div className="flex justify-between items-center mb-2 gap-2">
          <div className="flex items-center gap-2">
            {((data?.file_type || data?.masked_content?.mime_type || '').startsWith('image/')) && (
              <>
                <Button size="sm" type="button" variant="outline" onClick={stop(() => {
                  const b64 = data?.masked_content?.base64_data; if (!b64) return;
                  navigator.clipboard?.writeText(b64).then(() => { try { toast({ title: 'Copied to clipboard' }); } catch {} }).catch(() => {
                    const ta = document.createElement('textarea'); ta.value = b64; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
                    try { toast({ title: 'Copied to clipboard' }); } catch {}
                  });
                })}>Copy Original Base64</Button>
                {Boolean(data?.masked_content?.redacted_image_base64) && (
                  <Button size="sm" type="button" variant="outline" onClick={stop(() => {
                    const b64 = data?.masked_content?.redacted_image_base64; if (!b64) return;
                    navigator.clipboard?.writeText(b64).then(() => { try { toast({ title: 'Copied to clipboard' }); } catch {} }).catch(() => {
                      const ta = document.createElement('textarea'); ta.value = b64; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
                      try { toast({ title: 'Copied to clipboard' }); } catch {}
                    });
                  })}>Copy Redacted Base64</Button>
                )}
              </>
            )}
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Button size="sm" type="button" variant="outline" onClick={stop(() => { if (data) { downloadJson(`${fileName}.masked.json`, data); try { toast({ title: 'Downloaded JSON' }); } catch {} } })}>
              <Download className="h-4 w-4 mr-2" />
              Download JSON
            </Button>
          </div>
        </div>
        <pre className="max-h-[60vh] overflow-auto bg-muted p-3 rounded text-xs whitespace-pre-wrap break-words">{JSON.stringify(formatDataForDisplay(data), null, 2)}</pre>
      </div>
    );
  };

  const MaskedDataDialog = ({ record }: { record: any }) => (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button>
      </DialogTrigger>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Masked Data Preview</DialogTitle>
          <DialogDescription>{record.fileName} - Processed on {record.date}</DialogDescription>
        </DialogHeader>
        <MaskedJson maskingId={record.id} fileName={record.fileName} />
      </DialogContent>
    </Dialog>
  );

  const AnalysisDataDialog = ({ record }: { record: any }) => {
    const [data, setData] = useState<any | null>(null);

    useEffect(() => {
      (async () => {
        try {
          const res = await apiGetAnalysis(record.id);
          setData(res);
        } catch (err) {
          console.error('Failed to load analysis details', err);
          setData({ error: 'Failed to load' });
        }
      })();
    }, [record.id]);

    const derived = (() => {
      const d = data || {};
      const dataQuality =
        d?.scores?.quality ?? d?.quality ?? d?.metrics?.data_quality ?? d?.dataQuality ?? null;
      const riskLevel =
        d?.risk?.level ?? d?.riskLevel ?? d?.scores?.risk_level ?? d?.risk ?? null;
      const sensitiveFields =
        (Array.isArray(d?.sensitive_fields) ? d?.sensitive_fields?.length : null) ??
        d?.metrics?.sensitive_fields ??
        d?.sensitiveFields ??
        null;
      const compliance =
        d?.compliance ?? d?.standards ?? d?.badges ?? [];
      return { dataQuality, riskLevel, sensitiveFields, compliance };
    })();

    return (
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button>
        </DialogTrigger>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Analysis Results</DialogTitle>
            <DialogDescription>{record.fileName} - Analyzed on {record.date}</DialogDescription>
          </DialogHeader>
          <div className="flex items-center justify-between mb-2 gap-2">
            <div />
            <div className="flex items-center gap-2 flex-wrap">
              <Button size="sm" type="button" variant="outline" onClick={async (e) => {
                e.preventDefault(); e.stopPropagation();
                try {
                  const full = data ?? await apiGetAnalysis(record.id);
                  downloadJson(`${record.fileName}.analysis.json`, full);
                } catch (err) {
                  console.error('Download analysis JSON failed:', err);
                }
              }}>
                <Download className="h-4 w-4 mr-2" />
                Download JSON
              </Button>
            </div>
          </div>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className="text-2xl font-bold text-data-analysis">
                  {derived.dataQuality ?? '—'}
                </p>
                <p className="text-xs text-muted-foreground">Data Quality</p>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className="text-2xl font-bold text-warning">
                  {derived.riskLevel ?? '—'}
                </p>
                <p className="text-xs text-muted-foreground">Risk Level</p>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-sm mb-2">Sensitive Fields Found:</h4>
              <p className="text-2xl font-bold text-destructive">
                {derived.sensitiveFields ?? '—'}
              </p>
            </div>
            <div>
              <h4 className="font-medium text-sm mb-2">Compliance Standards:</h4>
              <div className="flex flex-wrap gap-1">
                {(derived.compliance as any[]).map((standard: any, index: number) => (
                  <Badge key={index} variant="outline">
                    {typeof standard === 'string' ? standard : (standard?.name ?? JSON.stringify(standard))}
                  </Badge>
                ))}
              </div>
            </div>
            <pre className="max-h-[50vh] overflow-auto bg-muted p-3 rounded text-xs whitespace-pre-wrap break-words">
              {data ? JSON.stringify(data, null, 2) : 'Loading...'}
            </pre>
          </div>
        </DialogContent>
      </Dialog>
    );
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Processing History
              {filter && (<Badge variant="outline" className="ml-2">{filter === 'mask' ? 'Masking Only' : 'Analysis Only'}</Badge>)}
            </CardTitle>
            <CardDescription>Track all your data processing activities</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" type="button" onClick={async (e) => { e.preventDefault(); e.stopPropagation(); await loadHistory(); try { toast({ title: 'Refreshed' }); } catch {} }}>Refresh</Button>
            <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-2" />Export</Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search files..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
          </div>
          <Button variant="outline" size="sm"><Filter className="h-4 w-4 mr-2" />Filter</Button>
          <Button variant="outline" size="sm"><Calendar className="h-4 w-4 mr-2" />Date Range</Button>
        </div>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">#</TableHead>
                <TableHead>File Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Time</TableHead>
                <TableHead className="text-center">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">No records found</TableCell>
                </TableRow>
              ) : (
                filteredData.map((record, index) => (
                  <TableRow key={record.id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell><div className="flex items-center gap-2"><FileText className="h-4 w-4 text-muted-foreground" />{record.fileName}</div></TableCell>
                    <TableCell>{getTypeBadge(record.type, record.reversible)}</TableCell>
                    <TableCell>{getStatusBadge(record.status)}</TableCell>
                    <TableCell>{record.date}</TableCell>
                    <TableCell>{record.time}</TableCell>
                    <TableCell>
                      <div className="flex items-center justify-center gap-1">
                        {record.status === 'completed' && (
                            record.type === 'mask' ? (
                              <>
                                <MaskedDataDialog record={record} />
                                 <Button variant="ghost" size="sm" type="button" onClick={async (e) => { e.preventDefault(); e.stopPropagation(); try { const data = await apiGetMasked(record.id); downloadJson(`${record.fileName}.masked.json`, data); } catch (error) { console.error('Download error:', error); } }}>
                                  <Download className="h-4 w-4" />
                                </Button>
                              </>
                            ) : (
                              <>
                                <AnalysisDataDialog record={record} />
                                <Button variant="ghost" size="sm" type="button" onClick={async (e) => { e.preventDefault(); e.stopPropagation(); try { const data = await apiGetAnalysis(record.id); downloadJson(`${record.fileName}.analysis.json`, data); } catch (error) { console.error('Download error:', error); } }}>
                                  <Download className="h-4 w-4" />
                                </Button>
                              </>
                            )
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default HistoryTable;
