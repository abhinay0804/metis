import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, Eye, EyeOff, Lock, ArrowLeft } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { apiLogin } from "@/lib/api";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg("");
    try {
      const data = await apiLogin(email, password);
      localStorage.setItem('idToken', data.access_token);
      
      const searchParams = new URLSearchParams(location.search);
      if (searchParams.get('demo') === 'true') {
        localStorage.removeItem('metis_tour_completed');
      }
      
      toast({ title: "Login Successful", description: "Welcome to Metis" });
      navigate("/dashboard");
    } catch (err: any) {
      setErrorMsg("Invalid credentials entered. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-slate-50 dark:via-slate-900 to-blue-50/30 dark:to-blue-900/30 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          className="mb-6"
          onClick={() => navigate("/")}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Home
        </Button>

        {/* Logo and Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-2xl mb-4 shadow-large">
            <Shield className="w-8 h-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold text-foreground">Metis</h1>
          <p className="text-muted-foreground font-medium mt-2">Secure Data Masking & Analysis Platform</p>
        </div>

        {/* Login Form */}
        <Card className="shadow-large border-0">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Sign In</CardTitle>
            <CardDescription>
              Access your secure dashboard to manage data masking and analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-6">
              {errorMsg && (
                <div className="p-3 text-sm font-medium text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30 rounded-md border border-red-200 dark:border-red-800">
                  {errorMsg}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="h-12"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="h-12 pr-12"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-12 px-3 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </div>
              </div>

              <Button 
                type="submit" 
                variant="security"
                className="w-full h-12" 
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                    Signing In...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Lock className="w-4 h-4" />
                    Sign In Securely
                  </div>
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-muted-foreground">
                Don't have an account?{" "}
                <button 
                  onClick={() => navigate("/signup")}
                  className="text-primary hover:text-primary/80 font-medium"
                >
                  Sign up here
                </button>
              </p>
              <button 
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  if (!email) {
                    toast({ 
                      title: "Email Required", 
                      description: "Please enter your email address first to reset your password.",
                      variant: "destructive"
                    });
                  } else {
                    toast({ 
                      title: "Reset Link Sent", 
                      description: `If an account exists for ${email}, a password reset link will be sent.` 
                    });
                  }
                }}
                className="text-xs text-primary hover:text-primary/80 transition-colors block mt-2 mx-auto"
              >
                Forgot your password?
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Security Notice */}
        <div className="mt-6 text-center text-xs text-muted-foreground">
          <p>Protected by enterprise-grade security</p>
        </div>
      </div>
    </div>
  );
};

export default Login;