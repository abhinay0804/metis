import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { 
  Shield, 
  BarChart3, 
  Eye, 
  Download, 
  Clock, 
  CheckCircle,
  AlertTriangle,
  FileText
} from "lucide-react";

interface ProcessingResultsProps {
  results: any;
  type: 'mask' | 'analysis';
  onSecondaryAction: (type: 'mask' | 'analysis') => void;
}

const ProcessingResults = ({ results, type, onSecondaryAction }: ProcessingResultsProps) => {
  if (type === 'mask') {
    return (
      <Card className="border-data-mask/20 bg-gradient-to-br from-background to-data-mask/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-data-mask">
            <Shield className="h-5 w-5" />
            Data Masking Complete
          </CardTitle>
          <CardDescription>
            Sensitive data has been successfully masked and secured
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-card rounded-lg">
              <p className="text-2xl font-bold text-data-mask">{results.maskedFields.length}</p>
              <p className="text-xs text-muted-foreground">Fields Masked</p>
            </div>
            <div className="text-center p-3 bg-card rounded-lg">
              <p className="text-2xl font-bold text-success">{results.confidence}%</p>
              <p className="text-xs text-muted-foreground">Confidence</p>
            </div>
            <div className="text-center p-3 bg-card rounded-lg">
              <p className="text-2xl font-bold text-primary">{results.processingTime}</p>
              <p className="text-xs text-muted-foreground">Processing Time</p>
            </div>
            <div className="text-center p-3 bg-card rounded-lg">
              <p className="text-2xl font-bold text-foreground">{(results.originalSize / 1024).toFixed(1)}KB</p>
              <p className="text-xs text-muted-foreground">File Size</p>
            </div>
          </div>

          <Separator />

          {/* Masked Data Preview */}
          <div>
            <h4 className="font-semibold flex items-center gap-2 mb-3">
              <Eye className="h-4 w-4" />
              Masked Data Preview
            </h4>
            <div className="space-y-2">
              {Object.entries(results.maskedData).map(([field, value]) => (
                <div key={field} className="flex justify-between items-center p-3 bg-muted rounded-lg">
                  <span className="font-medium capitalize">{field.replace('_', ' ')}</span>
                  <Badge variant="secondary" className="font-mono text-xs max-w-xs truncate">
                    {typeof value === 'string' ? 
                      (value.length > 50 ? `${value.substring(0, 50)}...` : value) :
                     Array.isArray(value) ? `${value.length} items` :
                     typeof value === 'object' ? `${Object.keys(value).length} properties` :
                     String(value)}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <Button 
              variant="analysis"
              onClick={() => onSecondaryAction('analysis')}
              className="flex-1"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Analyze Masked Data
            </Button>
            <Button variant="outline" className="flex-1">
              <Download className="h-4 w-4 mr-2" />
              Download Report
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-data-analysis/20 bg-gradient-to-br from-background to-data-analysis/5">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-data-analysis">
          <BarChart3 className="h-5 w-5" />
          Data Analysis Complete
        </CardTitle>
        <CardDescription>
          Comprehensive analysis of your data structure and security posture
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* File Description */}
        <div>
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <FileText className="h-4 w-4" />
            File Description
          </h4>
          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm leading-relaxed">{results.description}</p>
          </div>
        </div>

        <Separator />

        {/* Key Findings */}
        <div>
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Key Findings
          </h4>
          <div className="space-y-2">
            {results.keyFindings.map((finding: string, index: number) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-muted rounded-lg">
                <div className="w-2 h-2 bg-data-analysis rounded-full mt-2 flex-shrink-0" />
                <span className="text-sm">{finding}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Legacy format support - show if available */}
        {results.dataQuality && (
          <>
            <Separator />
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="font-medium">Data Quality Score</span>
                <span className="text-2xl font-bold text-data-analysis">{results.dataQuality}%</span>
              </div>
              <Progress value={results.dataQuality} className="h-2" />
            </div>
          </>
        )}

        {results.riskLevel && (
          <>
            <Separator />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-card rounded-lg">
                <AlertTriangle className={`h-8 w-8 mx-auto mb-2 ${
                  results.riskLevel === 'Low' ? 'text-success' : 
                  results.riskLevel === 'Medium' ? 'text-warning' : 'text-destructive'
                }`} />
                <p className="font-semibold">{results.riskLevel} Risk</p>
                <p className="text-sm text-muted-foreground">Security Level</p>
              </div>
              {results.sensitiveFields && (
                <div className="text-center p-4 bg-card rounded-lg">
                  <FileText className="h-8 w-8 mx-auto mb-2 text-data-analysis" />
                  <p className="font-semibold">{results.sensitiveFields}</p>
                  <p className="text-sm text-muted-foreground">Sensitive Fields</p>
                </div>
              )}
              {results.compliance && results.compliance.length > 0 && (
                <div className="text-center p-4 bg-card rounded-lg">
                  <CheckCircle className="h-8 w-8 mx-auto mb-2 text-success" />
                  <p className="font-semibold">{results.compliance.length}</p>
                  <p className="text-sm text-muted-foreground">Compliance Standards</p>
                </div>
              )}
            </div>
          </>
        )}

        {/* Compliance Standards */}
        {results.compliance && results.compliance.length > 0 && (
          <div>
            <h4 className="font-semibold mb-3">Compliance Standards</h4>
            <div className="flex flex-wrap gap-2">
              {results.compliance.map((standard: string, index: number) => (
                <Badge key={index} variant="default">
                  {standard}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {results.recommendations && results.recommendations.length > 0 && (
          <div>
            <h4 className="font-semibold mb-3">Security Recommendations</h4>
            <div className="space-y-2">
              {results.recommendations.map((rec: string, index: number) => (
                <div key={index} className="flex items-start gap-2 p-3 bg-muted rounded-lg">
                  <CheckCircle className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <Button 
            variant="mask"
            onClick={() => onSecondaryAction('mask')}
            className="flex-1"
          >
            <Shield className="h-4 w-4 mr-2" />
            Apply Data Masking
          </Button>
          <Button variant="outline" className="flex-1">
            <Download className="h-4 w-4 mr-2" />
            Export Analysis
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProcessingResults;