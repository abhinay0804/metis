import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
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
import { useLocation } from "react-router-dom";
import FileUpload from "@/components/FileUpload";
import { apiProcess, apiAnalyze, apiStats } from "@/lib/api";
import HistoryTable from "@/components/HistoryTable";
import DashboardLayout from "@/components/DashboardLayout";
import ProcessingResults from "@/components/ProcessingResults";
import AnalysisList from "@/components/AnalysisList";
import { Joyride, Step } from "react-joyride";

const Dashboard = () => {
  const location = useLocation();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [processProgress, setProcessProgress] = useState(0);
  const [results, setResults] = useState<any>(null);
  const [processType, setProcessType] = useState<'mask' | 'analysis' | null>(null);
  const [maskedJson, setMaskedJson] = useState<any>(null);
  const [refreshHistory, setRefreshHistory] = useState(0);
  const [activeTab, setActiveTab] = useState('history');
  const [isReversible, setIsReversible] = useState(true);
  
  const [userStats, setUserStats] = useState({
    total_jobs: 0,
    completed_jobs: 0,
    failed_jobs: 0,
    avg_processing_time_ms: 0,
    total_pii_detections: 0
  });

  const topRef = useRef<HTMLDivElement | null>(null);
  const tabsRef = useRef<HTMLDivElement | null>(null);
  const { toast } = useToast();

  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false);
  const [tempApiKey, setTempApiKey] = useState('');
  
  const [runTour, setRunTour] = useState(false);
  
  useEffect(() => {
    // Check if user has seen the tour
    const hasSeenTour = localStorage.getItem('metis_tour_completed');
    if (!hasSeenTour) {
      // Small delay to ensure all DOM elements and animations are finished rendering
      setTimeout(() => {
        setRunTour(true);
      }, 1000);
    }

    // Fetch user stats
    const fetchStats = async () => {
      try {
        const stats = await apiStats();
        setUserStats(stats);
      } catch (err) {
        console.error("Failed to fetch stats", err);
      }
    };
    fetchStats();
  }, [refreshHistory]);

  const handleJoyrideCallback = (data: any) => {
    const { status } = data;
    const finishedStatuses = ['finished', 'skipped'];
    if (finishedStatuses.includes(status)) {
      setRunTour(false);
      localStorage.setItem('metis_tour_completed', 'true');
    }
  };

  const tourSteps: Step[] = [
    {
      target: '.tour-upload',
      content: 'Welcome to Metis! Start by securely uploading your files here for masking or analysis.',
      disableBeacon: true,
    },
    {
      target: '.tour-stats',
      content: 'Track your overall data protection metrics and compliance score in real-time.',
    },
    {
      target: '.tour-actions',
      content: 'Quickly export reports and view security logs here.',
    },
    {
      target: '.tour-history',
      content: 'Access your processing history, masked data, and detailed analysis reports.',
    }
  ];

  useEffect(() => {
    if (location.pathname === '/masking') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      toast({ title: "Ready for Data Masking", description: "Upload a file to begin masking.", duration: 2000 });
    } else if (location.pathname === '/analysis') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      toast({ title: "Ready for Analysis", description: "Upload a file to begin analysis.", duration: 2000 });
    } else if (location.pathname === '/history') {
      setActiveTab('history');
      tabsRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [location.pathname]);

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
    setProcessProgress(0);
    topRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    try {
      const resp = await apiProcess(selectedFile, true, undefined, (p) => setProcessProgress(p));
      const stats = resp.detection_summary || {};
      const totalMasked = stats.total_detections || 0;
      const confidence = stats.confidence_score ? Math.round(stats.confidence_score * 100) : 100;
      const pTime = resp.processing_time_ms ? `${(resp.processing_time_ms / 1000).toFixed(2)}s` : '—';
      
      setMaskedJson(resp.masked);
      setResults({
        originalSize: selectedFile.size,
        maskedFields: new Array(totalMasked).fill(0),
        maskedData: resp.masked,
        confidence: confidence,
        processingTime: pTime
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

    if (type === 'analysis') {
      const storedKey = localStorage.getItem('geminiApiKey');
      if (!storedKey) {
        setShowApiKeyDialog(true);
        return;
      }
    }

    setProcessing(true);
    setProcessType(type);
    setProcessProgress(0);
    setResults(null);
    topRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    try {
      if (type === 'mask') {
        const resp = await apiProcess(selectedFile, isReversible, undefined, (p) => setProcessProgress(p));
        const stats = resp.detection_summary || {};
        const totalMasked = stats.total_detections || 0;
        const confidence = stats.confidence_score ? Math.round(stats.confidence_score * 100) : 100;
        const pTime = resp.processing_time_ms ? `${(resp.processing_time_ms / 1000).toFixed(2)}s` : '—';

        setMaskedJson(resp.masked);
        setResults({
          originalSize: selectedFile.size,
          maskedFields: new Array(totalMasked).fill(0),
          maskedData: resp.masked,
          confidence: confidence,
          processingTime: pTime
        });
        setRefreshHistory(prev => prev + 1); // Trigger history refresh
        toast({ title: 'Masking Complete', description: `${selectedFile.name} processed` });
      } else {
        // Simulate progress for analysis since it is synchronous currently
        setProcessProgress(20);
        const timer = setInterval(() => setProcessProgress(p => Math.min(p + 15, 90)), 800);
        (window as any)._analysisTimer = timer;
        const resp = await apiAnalyze(selectedFile);
        clearInterval(timer);
        (window as any)._analysisTimer = null;
        setProcessProgress(100);
        setResults(resp);
        setRefreshHistory(prev => prev + 1); // Trigger history refresh
        toast({ title: 'Analysis Complete', description: `${selectedFile.name} analyzed` });
      }
    } catch (e: any) {
      const errMsg = e?.message || 'Error';
      
      let timerInstance = (window as any)._analysisTimer;
      if (timerInstance) clearInterval(timerInstance);
      
      const isAuthError = errMsg.includes('API_KEY_INVALID') || errMsg.includes('API key not valid') || errMsg.includes('403');
      
      if (isAuthError) {
        localStorage.removeItem('geminiApiKey');
        setShowApiKeyDialog(true);
        toast({ title: 'Invalid API Key', description: 'Your Gemini API Key is invalid or expired. Please enter a valid key.', variant: 'destructive' });
      } else if (errMsg.includes('503') || errMsg.includes('high demand') || errMsg.includes('UNAVAILABLE')) {
        toast({ title: 'Service Overloaded', description: 'The Google Gemini AI service is currently experiencing high demand. Please try again in a few moments.', variant: 'destructive' });
      } else {
        toast({ title: 'Processing failed', description: errMsg, variant: 'destructive' });
      }
    } finally {
      setProcessing(false);
    }
  };

  const handleSaveApiKey = () => {
    if (tempApiKey.trim()) {
      localStorage.setItem('geminiApiKey', tempApiKey.trim());
      setShowApiKeyDialog(false);
      handleProcess('analysis');
    } else {
      toast({ title: 'Invalid API Key', description: 'Please enter a valid Gemini API Key', variant: 'destructive' });
    }
  };

  const stats = [
    {
      title: "Files Processed",
      value: userStats.total_jobs.toString(),
      change: userStats.total_jobs === 0 ? "Start processing!" : "Total jobs run",
      icon: FileText,
      color: "text-primary"
    },
    {
      title: "Data Masked",
      value: userStats.total_pii_detections.toString(),
      change: "Entities redacted in last 30 days",
      icon: Shield,
      color: "text-security-accent"
    },
    {
      title: "Success Rate",
      value: userStats.total_jobs > 0 ? `${Math.round((userStats.completed_jobs / userStats.total_jobs) * 100)}%` : "0%",
      change: "Completion rate in last 30 days",
      icon: CheckCircle,
      color: "text-success"
    },
    {
      title: "Avg Time",
      value: userStats.avg_processing_time_ms ? `${(userStats.avg_processing_time_ms / 1000).toFixed(1)}s` : "0s",
      change: "Processing latency in last 30 days",
      icon: Clock,
      color: "text-data-analysis"
    }
  ];

  return (
    <DashboardLayout>
      <Joyride
        steps={tourSteps}
        run={runTour}
        continuous={true}
        showProgress={true}
        showSkipButton={true}
        callback={handleJoyrideCallback}
        styles={{
          options: {
            primaryColor: '#3b82f6',
            textColor: '#1e293b',
            backgroundColor: '#ffffff',
          }
        }}
      />
      <div className="space-y-6" ref={topRef}>
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">
            Secure data masking and analysis platform
          </p>
        </div>

        {/* Stats Cards */}
        <div className="tour-stats grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
                        {stat.change}
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
          <div className="lg:col-span-2 tour-upload">
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
                    
                    <div className="flex items-center space-x-2 py-2">
                      <Switch id="reversible-mode" checked={isReversible} onCheckedChange={setIsReversible} />
                      <Label htmlFor="reversible-mode" className="text-sm font-medium">
                        Enable Reversible Masking (Allows authorized unmasking)
                      </Label>
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
                    {processing && processProgress > 0 && (
                      <div className="space-y-1 mt-4">
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Processing...</span>
                          <span>{processProgress}%</span>
                        </div>
                        <Progress value={processProgress} className="h-2" />
                      </div>
                    )}
                    {results && processType && (
                      <ProcessingResults 
                        results={results} 
                        type={processType}
                        onSecondaryAction={() => handleProcess(processType === 'mask' ? 'analysis' : 'mask')}
                      />
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="tour-actions">
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks and shortcuts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={async () => {
                    try {
                      toast({ title: "Exporting Report", description: "Preparing your data..." });
                      const { apiHistory } = await import('@/lib/api');
                      const history = await apiHistory();
                      const blob = new Blob([JSON.stringify(history, null, 2)], { type: 'application/json' });
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `metis-report-${new Date().toISOString().split('T')[0]}.json`;
                      a.click();
                      window.URL.revokeObjectURL(url);
                      toast({ title: "Export Complete", description: "Your report has been downloaded." });
                    } catch (err) {
                      toast({ title: "Export Failed", description: "Failed to generate report.", variant: "destructive" });
                    }
                  }}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export Report
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => {
                    setActiveTab("history");
                    setTimeout(() => tabsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150);
                  }}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  View Logs
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => {
                    setActiveTab("analysis");
                    setTimeout(() => tabsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150);
                    toast({ title: "Compliance Check", description: "View your risk levels and compliance warnings in the Analysis tab.", variant: "default" });
                  }}
                >
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Compliance Check
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* History Section */}
        <div ref={tabsRef} className="tour-history">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList>
              <TabsTrigger value="history">Processing History</TabsTrigger>
              <TabsTrigger value="masked">Masked Data</TabsTrigger>
              <TabsTrigger value="analysis">Analysis Reports</TabsTrigger>
            </TabsList>
          
          <TabsContent value="history" className="mt-6">
            <HistoryTable refreshTrigger={refreshHistory} onFilterChange={() => setActiveTab('masked')} />
          </TabsContent>
          
          <TabsContent value="masked" className="mt-6">
            <HistoryTable filter="mask" refreshTrigger={refreshHistory} onFilterChange={() => setActiveTab('analysis')} />
          </TabsContent>
          
          <TabsContent value="analysis" className="mt-6">
            <AnalysisList refreshTrigger={refreshHistory} onFilterChange={() => setActiveTab('history')} />
          </TabsContent>
          </Tabs>
        </div>
      </div>

      <Dialog open={showApiKeyDialog} onOpenChange={setShowApiKeyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Enter Gemini API Key</DialogTitle>
            <DialogDescription>
              To use genuine LLM-driven content analysis, please enter your Google Gemini API Key. 
              This key is stored securely in your browser's local storage and is only used to authenticate your analysis requests.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input 
              type="password"
              placeholder="AIzaSy..." 
              value={tempApiKey}
              onChange={(e) => setTempApiKey(e.target.value)}
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowApiKeyDialog(false)}>Cancel</Button>
            <Button onClick={handleSaveApiKey}>Save & Analyze</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default Dashboard;