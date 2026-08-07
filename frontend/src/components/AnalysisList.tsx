import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { FileText, Eye, Download, Filter, Search, Calendar, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

import { apiAnalyze, apiListAnalyses, apiGetAnalysis } from "@/lib/api";

interface AnalysisListItem {
  analysis_id: string;
  file_name: string;
  file_type: string;
  created_at?: string;
}

const AnalysisList = ({ refreshTrigger = 0, onFilterChange }: { refreshTrigger?: number, onFilterChange?: () => void }) => {
  const [rows, setRows] = useState<AnalysisListItem[]>([]);
  const { toast } = useToast();

  const [searchTerm, setSearchTerm] = useState("");
  const [dateRange, setDateRange] = useState<{from: string, to: string}>({from: '', to: ''});

  const loadData = async () => {
    try {
      const list = await apiListAnalyses();
      setRows(list);
    } catch (e) {
      setRows([]);
    }
  };

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const exportToCsv = () => {
    if (filteredData.length === 0) {
      toast({ title: 'No data to export', variant: 'destructive' });
      return;
    }
    const headers = ['ID', 'File Name', 'Type', 'Status', 'Date', 'Time'];
    const csvRows = filteredData.map(item => {
      const dt = item.created_at ? new Date(item.created_at) : null;
      const dateStr = dt ? dt.toISOString().slice(0,10) : '';
      const timeStr = dt ? dt.toLocaleTimeString() : '';
      return [item.analysis_id, item.file_name, item.file_type, 'completed', dateStr, timeStr];
    });
    const csvContent = [headers, ...csvRows].map(e => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `metis_analysis_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    toast({ title: 'Exported analysis history to CSV' });
  };

  const filteredData = rows
    .filter((item) => item.file_name.toLowerCase().includes(searchTerm.toLowerCase()))
    .filter((item) => {
      if (!dateRange.from && !dateRange.to) return true;
      const d = new Date(item.created_at || 0);
      d.setHours(0, 0, 0, 0);
      const fromD = dateRange.from ? new Date(dateRange.from + 'T00:00:00') : null;
      if (fromD) fromD.setHours(0, 0, 0, 0);
      const toD = dateRange.to ? new Date(dateRange.to + 'T00:00:00') : null;
      if (toD) toD.setHours(23, 59, 59, 999);
      if (fromD && d < fromD) return false;
      if (toD && d > toD) return false;
      return true;
    });

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
          const res = await apiGetAnalysis(id);
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
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" /> File Analysis
              <Badge variant="outline" className="ml-2">Analysis Only</Badge>
            </CardTitle>
            <CardDescription>Summary of analyzed files</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" type="button" onClick={async (e) => { e.preventDefault(); e.stopPropagation(); await loadData(); try { toast({ title: 'Refreshed' }); } catch {} }}>
              <RefreshCw className="h-4 w-4 mr-2" /> Refresh
            </Button>
            <Button variant="outline" size="sm" onClick={exportToCsv}>
              <Download className="h-4 w-4 mr-2" /> Export
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search files..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
          </div>
          <Button variant="outline" size="sm" onClick={() => {
            if (onFilterChange) onFilterChange();
          }}>
            <Filter className="h-4 w-4 mr-2" />
            Filter: Analysis
          </Button>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" size="sm">
                <Calendar className="h-4 w-4 mr-2" />
                {dateRange.from || dateRange.to ? 'Range Applied' : 'Date Range'}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="grid gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium leading-none">Filter by Date</h4>
                  <p className="text-sm text-muted-foreground">Set a start and end date.</p>
                </div>
                <div className="grid gap-2">
                  <div className="grid grid-cols-3 items-center gap-4">
                    <label htmlFor="from-analysis" className="text-sm">From</label>
                    <Input id="from-analysis" type="date" value={dateRange.from} onChange={(e) => setDateRange(p => ({...p, from: e.target.value}))} className="col-span-2 h-8" />
                  </div>
                  <div className="grid grid-cols-3 items-center gap-4">
                    <label htmlFor="to-analysis" className="text-sm">To</label>
                    <Input id="to-analysis" type="date" value={dateRange.to} onChange={(e) => setDateRange(p => ({...p, to: e.target.value}))} className="col-span-2 h-8" />
                  </div>
                  <Button size="sm" variant="outline" onClick={() => setDateRange({from: '', to: ''})} className="mt-2">Clear Dates</Button>
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
        
        {filteredData.length === 0 ? (
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
                {filteredData.map((r, idx) => {
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
                            try {
                              const data = await apiGetAnalysis(r.analysis_id);
                              const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                              const url = URL.createObjectURL(blob);
                              const a = document.createElement('a'); a.href = url; a.download = `${r.file_name}.analysis.json`; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
                            } catch (err) {
                              console.error(err);
                            }
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
