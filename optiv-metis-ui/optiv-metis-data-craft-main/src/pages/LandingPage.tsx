import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Shield, 
  BarChart3, 
  Lock, 
  CheckCircle, 
  Users, 
  Globe,
  Zap,
  Award,
  ArrowRight,
  Eye,
  FileText,
  TrendingUp
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const LandingPage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Shield,
      title: "Advanced Data Masking",
      description: "Protect sensitive information with enterprise-grade masking algorithms that maintain data utility while ensuring privacy."
    },
    {
      icon: BarChart3,
      title: "Intelligent Analysis",
      description: "Comprehensive data analysis with AI-powered insights to identify risks and compliance gaps in your datasets."
    },
    {
      icon: Lock,
      title: "Enterprise Security",
      description: "Bank-level security with end-to-end encryption, audit trails, and compliance with global privacy standards."
    },
    {
      icon: Zap,
      title: "Real-time Processing",
      description: "Lightning-fast processing capabilities that handle large datasets without compromising on accuracy or security."
    },
    {
      icon: Eye,
      title: "Compliance Monitoring",
      description: "Automated compliance checking against GDPR, HIPAA, PCI-DSS, and other regulatory frameworks."
    },
    {
      icon: Users,
      title: "Team Collaboration",
      description: "Secure workspace for teams with role-based access controls and collaborative data protection workflows."
    }
  ];

  const stats = [
    { value: "99.9%", label: "Data Protection Accuracy", icon: Shield },
    { value: "500M+", label: "Records Processed", icon: FileText },
    { value: "150+", label: "Enterprise Clients", icon: Users },
    { value: "24/7", label: "Security Monitoring", icon: TrendingUp }
  ];

  const complianceStandards = [
    "GDPR", "HIPAA", "PCI-DSS", "SOX", "CCPA", "ISO 27001"
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center bg-primary rounded-xl">
              <Shield className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Optiv Metis</h1>
              <p className="text-xs text-muted-foreground">by Optiv Security Inc.</p>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm font-medium hover:text-primary transition-colors">Features</a>
            <a href="#security" className="text-sm font-medium hover:text-primary transition-colors">Security</a>
            <a href="#compliance" className="text-sm font-medium hover:text-primary transition-colors">Compliance</a>
            <a href="#contact" className="text-sm font-medium hover:text-primary transition-colors">Contact</a>
          </nav>

          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => navigate("/login")}>
              Sign In
            </Button>
            <Button variant="security" onClick={() => navigate("/signup")}>
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-background via-slate-50/50 to-blue-50/30 py-20">
        <div className="container relative">
          <div className="mx-auto max-w-4xl text-center">
            <Badge variant="secondary" className="mb-6">
              <Award className="h-3 w-3 mr-1" />
              Trusted by Fortune 500 Companies
            </Badge>
            
            <h1 className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
              Secure Your Data with 
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Advanced Masking</span>
            </h1>
            
            <p className="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto">
              Enterprise-grade data masking and analysis platform that protects sensitive information 
              while maintaining data utility for analytics and development workflows.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" variant="security" className="text-lg px-8 py-4" onClick={() => navigate("/signup")}>
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-4" onClick={() => navigate("/demo")}>
                Watch Demo
              </Button>
            </div>

            <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <div key={index} className="text-center">
                    <Icon className="h-8 w-8 mx-auto mb-2 text-primary" />
                    <div className="text-2xl font-bold text-foreground">{stat.value}</div>
                    <div className="text-sm text-muted-foreground">{stat.label}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-background">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Comprehensive Data Protection Suite
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to secure, analyze, and manage sensitive data across your organization.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="border-0 shadow-medium hover:shadow-large transition-all duration-300">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center bg-primary/10 rounded-xl">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <CardTitle className="text-xl">{feature.title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Security & Compliance Section */}
      <section id="compliance" className="py-20 bg-slate-50">
        <div className="container">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">
                Enterprise-Grade Security & Compliance
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                Built with security-first architecture and certified compliance with global privacy standards. 
                Protect your organization from data breaches and regulatory penalties.
              </p>
              
              <div className="space-y-4 mb-8">
                {[
                  "End-to-end encryption with AES-256",
                  "Zero-trust security architecture", 
                  "Automated audit trails and logging",
                  "SOC 2 Type II certified infrastructure"
                ].map((item, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <CheckCircle className="h-5 w-5 text-success flex-shrink-0" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>

              <div>
                <h3 className="font-semibold mb-4">Compliance Standards:</h3>
                <div className="flex flex-wrap gap-2">
                  {complianceStandards.map((standard, index) => (
                    <Badge key={index} variant="secondary" className="bg-primary/10 text-primary">
                      {standard}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <div className="relative">
              <Card className="p-8 border-0 shadow-large">
                <div className="text-center">
                  <div className="flex h-16 w-16 items-center justify-center bg-primary rounded-2xl mx-auto mb-4">
                    <Lock className="h-8 w-8 text-primary-foreground" />
                  </div>
                  <h3 className="text-2xl font-bold mb-2">Bank-Level Security</h3>
                  <p className="text-muted-foreground mb-6">
                    Your data is protected with military-grade encryption and security protocols 
                    used by the world's largest financial institutions.
                  </p>
                  <Button variant="outline" className="w-full">
                    <Globe className="h-4 w-4 mr-2" />
                    View Security Certifications
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="container text-center">
          <h2 className="text-3xl font-bold text-white sm:text-4xl mb-4">
            Ready to Secure Your Data?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of organizations protecting their sensitive data with Optiv Metis. 
            Start your free trial today and experience enterprise-grade data security.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button size="lg" variant="secondary" className="text-lg px-8 py-4" onClick={() => navigate("/signup")}>
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 py-4 border-white text-white hover:bg-white hover:text-blue-600" onClick={() => navigate("/contact")}>
              Contact Sales
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-background">
        <div className="container py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <div className="flex h-8 w-8 items-center justify-center bg-primary rounded-lg">
                  <Shield className="h-5 w-5 text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-bold">Optiv Metis</h3>
                  <p className="text-xs text-muted-foreground">by Optiv Security Inc.</p>
                </div>
              </div>
              <p className="text-muted-foreground mb-4 max-w-md">
                Leading the future of data protection with intelligent masking and analysis solutions 
                for enterprise security teams worldwide.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Security</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Integrations</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">API</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">About</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Support</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t mt-8 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              © 2024 Optiv Security Inc. All rights reserved.
            </p>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-foreground transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-foreground transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-foreground transition-colors">Cookie Policy</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;