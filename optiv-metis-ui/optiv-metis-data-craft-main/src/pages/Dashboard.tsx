import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Upload, 
  Shield, 
  BarChart3, 
  FileText, 
  Eye, 
  Download,
  Clock,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import FileUpload from "@/components/FileUpload";
import { apiProcess, apiAnalyze } from "@/lib/api";
import HistoryTable from "@/components/HistoryTable";
import DashboardLayout from "@/components/DashboardLayout";
import ProcessingResults from "@/components/ProcessingResults";
import AnalysisList from "@/components/AnalysisList";

const Dashboard = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [processType, setProcessType] = useState<'mask' | 'analysis' | null>(null);
  const [maskedJson, setMaskedJson] = useState<any>(null);
  const [refreshHistory, setRefreshHistory] = useState(0);
  const topRef = useRef<HTMLDivElement | null>(null);
  const { toast } = useToast();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setResults(null);
    setProcessType(null);
    toast({
      title: "File Selected",
      description: `${file.name} is ready for processing`,
    });
  };

  const handleReversibleMask = async () => {
    if (!selectedFile) {
      toast({
        title: "No File Selected",
        description: "Please upload a file first",
        variant: "destructive",
      });
      return;
    }
    setProcessing(true);
    setProcessType('mask');
    topRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    try {
      console.log('Processing file:', selectedFile.name, selectedFile.type);
      const resp = await apiProcess(selectedFile, true);
      console.log('Processing response:', resp);
      setMaskedJson(resp.masked);
      setResults({
        originalSize: selectedFile.size,
        maskedFields: [],
        maskedData: resp.masked,
        confidence: 100,
        processingTime: '—'
      });
      setRefreshHistory(prev => prev + 1); // Trigger history refresh
      toast({ title: 'Reversible Masking Complete', description: `${selectedFile.name} processed` });
    } catch (e: any) {
      console.error('Processing error:', e);
      toast({ title: 'Processing failed', description: e?.message || 'Error', variant: 'destructive' });
    } finally {
      setProcessing(false);
    }
  };

  const handleProcess = async (type: 'mask' | 'analysis') => {
    if (!selectedFile) {
      toast({
        title: "No File Selected",
        description: "Please upload a file first",
        variant: "destructive",
      });
      return;
    }

    setProcessing(true);
    setProcessType(type);
    topRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    try {
      if (type === 'mask') {
        console.log('Processing file (mask):', selectedFile.name, selectedFile.type);
        const resp = await apiProcess(selectedFile, false);
        console.log('Processing response (mask):', resp);
        setMaskedJson(resp.masked);
        setResults({
          originalSize: selectedFile.size,
          maskedFields: [],
          maskedData: resp.masked,
          confidence: 100,
          processingTime: '—'
        });
        setRefreshHistory(prev => prev + 1); // Trigger history refresh
        toast({ title: 'Masking Complete', description: `${selectedFile.name} processed` });
      } else {
        console.log('Starting analysis for:', selectedFile.name, selectedFile.type);
        const resp = await apiAnalyze(selectedFile);
        console.log('Analysis response received:', resp);
        setResults(resp);
        setRefreshHistory(prev => prev + 1); // Trigger history refresh
        toast({ title: 'Analysis Complete', description: `${selectedFile.name} analyzed` });
      }
    } catch (e: any) {
      toast({ title: 'Processing failed', description: e?.message || 'Error', variant: 'destructive' });
    } finally {
      setProcessing(false);
    }
  };

  const stats = [
    {
      title: "Files Processed",
      value: "1,247",
      change: "+12%",
      icon: FileText,
      color: "text-primary"
    },
    {
      title: "Data Masked",
      value: "98.5%",
      change: "+2.1%", 
      icon: Shield,
      color: "text-security-accent"
    },
    {
      title: "Compliance Score",
      value: "95%",
      change: "+5%",
      icon: CheckCircle,
      color: "text-success"
    },
    {
      title: "Processing Time",
      value: "1.2s",
      change: "-0.3s",
      icon: Clock,
      color: "text-data-analysis"
    }
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6" ref={topRef}>
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">
            Secure data masking and analysis platform
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index} className="hover:shadow-medium transition-all duration-300">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        {stat.title}
                      </p>
                      <p className="text-2xl font-bold text-foreground">
                        {stat.value}
                      </p>
                      <p className="text-xs text-success">
                        {stat.change} from last month
                      </p>
                    </div>
                    <Icon className={`h-8 w-8 ${stat.color}`} />
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* File Processing */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  File Processing
                </CardTitle>
                <CardDescription>
                  Upload files for masking or analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <FileUpload onFileSelect={handleFileSelect} />
                
                {selectedFile && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">{selectedFile.name}</span>
                      <Badge variant="secondary" className="ml-auto">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </Badge>
                    </div>
                    
                    <div className="flex gap-3 flex-wrap">
                      <Button 
                        variant="mask"
                        onClick={() => handleProcess('mask')}
                        disabled={processing}
                        className="flex-1"
                      >
                        <Shield className="h-4 w-4 mr-2" />
                        {processing && processType === 'mask' ? 'Masking...' : 'Mask Data'}
                      </Button>
                      <Button 
                        variant="analysis"
                        onClick={() => handleProcess('analysis')}
                        disabled={processing}
                        className="flex-1"
                        title="Analyze extracted content"
                      >
                        <BarChart3 className="h-4 w-4 mr-2" />
                        {processing && processType === 'analysis' ? 'Analyzing...' : 'Analyze Data'}
                      </Button>
                    </div>
                    {results && processType === 'analysis' && (
                      <ProcessingResults 
                        results={results} 
                        type={'analysis'}
                        onSecondaryAction={() => {}}
                      />
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks and shortcuts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <Download className="h-4 w-4 mr-2" />
                  Export Report
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Eye className="h-4 w-4 mr-2" />
                  View Logs
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Compliance Check
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* History Section */}
        <Tabs defaultValue="history" className="w-full">
          <TabsList>
            <TabsTrigger value="history">Processing History</TabsTrigger>
            <TabsTrigger value="masked">Masked Data</TabsTrigger>
            <TabsTrigger value="analysis">Analysis Reports</TabsTrigger>
          </TabsList>
          
          <TabsContent value="history" className="mt-6">
            <HistoryTable refreshTrigger={refreshHistory} />
          </TabsContent>
          
          <TabsContent value="masked" className="mt-6">
            <HistoryTable filter="mask" refreshTrigger={refreshHistory} />
          </TabsContent>
          
          <TabsContent value="analysis" className="mt-6">
            <AnalysisList refreshTrigger={refreshHistory} />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;