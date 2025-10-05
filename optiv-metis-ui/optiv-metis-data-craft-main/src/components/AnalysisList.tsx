import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FileText, Eye, Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

import { apiAnalyze, apiListAnalyses } from "@/lib/api";

interface AnalysisListItem {
  analysis_id: string;
  file_name: string;
  file_type: string;
  created_at?: string;
}

const AnalysisList = ({ refreshTrigger = 0 }: { refreshTrigger?: number }) => {
  const [rows, setRows] = useState<AnalysisListItem[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    (async () => {
      try {
        const list = await apiListAnalyses();
        setRows(list);
      } catch (e) {
        setRows([]);
      }
    })();
  }, [refreshTrigger]);

  const AnalysisDialog = ({ row }: { row: AnalysisListItem }) => (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" type="button"><Eye className="h-4 w-4" /></Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{row.file_name}</DialogTitle>
          <DialogDescription>{row.file_type}</DialogDescription>
        </DialogHeader>
        <AnalysisDetails id={row.analysis_id} fileName={row.file_name} />
      </DialogContent>
    </Dialog>
  );

  const AnalysisDetails = ({ id, fileName }: { id: string, fileName: string }) => {
    const [data, setData] = useState<any | null>(null);
    useEffect(() => {
      (async () => {
        try {
          const res = await fetch(`http://localhost:8001/analyses/${id}`).then(r => r.json());
          setData(res);
        } catch {
          setData({ error: 'Failed to load' });
        }
      })();
    }, [id]);

    if (!data) return <div className="text-sm text-muted-foreground">Loading…</div>;

    const desc = data?.result?.description || '—';
    const findings: string[] = data?.result?.keyFindings || [];

    const downloadJson = (filename: string, payload: any) => {
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    };

    return (
      <div className="space-y-3">
        <div className="flex justify-end">
          <Button size="sm" variant="outline" type="button" onClick={() => downloadJson(`${fileName}.analysis.json`, data)}>
            <Download className="h-4 w-4 mr-2" /> Download Analysis JSON
          </Button>
        </div>
        <div>
          <h4 className="font-medium">File Description</h4>
          <p className="text-sm text-muted-foreground mt-1">{desc}</p>
        </div>
        <div>
          <h4 className="font-medium">Key Findings</h4>
          <ul className="list-disc pl-5 text-sm mt-1">
            {findings.length === 0 ? <li>No key findings</li> : findings.map((f, i) => <li key={i}>{f}</li>)}
          </ul>
        </div>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" /> File Analysis
        </CardTitle>
        <CardDescription>Summary of analyzed files</CardDescription>
      </CardHeader>
      <CardContent>
        {rows.length === 0 ? (
          <div className="text-sm text-muted-foreground">No analysis records yet</div>
        ) : (
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
                {rows.map((r, idx) => {
                  const dt = r.created_at ? new Date(r.created_at) : null;
                  const dateStr = dt ? dt.toISOString().slice(0,10) : '';
                  const timeStr = dt ? dt.toLocaleTimeString() : '';
                  return (
                    <TableRow key={r.analysis_id}>
                      <TableCell className="font-medium">{idx + 1}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-muted-foreground" /> {r.file_name}
                        </div>
                      </TableCell>
                      <TableCell><Badge variant="secondary">{r.file_type}</Badge></TableCell>
                      <TableCell><Badge variant="default" className="bg-success">Completed</Badge></TableCell>
                      <TableCell>{dateStr}</TableCell>
                      <TableCell>{timeStr}</TableCell>
                      <TableCell>
                        <div className="flex items-center justify-center gap-1">
                          <AnalysisDialog row={r} />
                          <Button variant="ghost" size="sm" type="button" onClick={async (e) => {
                            e.preventDefault(); e.stopPropagation();
                            const data = await fetch(`http://localhost:8001/analyses/${r.analysis_id}`).then(r => r.json());
                            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a'); a.href = url; a.download = `${r.file_name}.analysis.json`; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
                          }}>
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AnalysisList;
