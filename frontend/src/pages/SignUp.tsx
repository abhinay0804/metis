import { useState } from "react";
import { apiRegister } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Shield, User, Mail, Building, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const SignUp = () => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    company: "",
    password: "",
    confirmPassword: ""
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const isLengthValid = formData.password.length >= 8;
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(formData.password);
  const passwordsMatch = formData.password === formData.confirmPassword && formData.password !== "";
  const isFormValid = isLengthValid && hasSpecialChar && passwordsMatch && formData.firstName && formData.lastName && formData.email && formData.company;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsLoading(true);
    
    try {
      if (formData.password !== formData.confirmPassword) {
        throw new Error("Passwords do not match");
      }
      
      const data = await apiRegister(
        formData.email, 
        formData.password, 
        `${formData.firstName} ${formData.lastName}`
      );
      localStorage.removeItem('metis_tour_completed');
      localStorage.setItem('idToken', data.access_token);
      
      toast({
        title: "Account Created Successfully",
        description: "Welcome to Metis! You're now logged in.",
      });
      
      navigate("/dashboard");
    } catch (err: any) {
      let errorMsg = "Could not create account";
      try {
        const parsed = JSON.parse(err.message);
        if (parsed.detail) errorMsg = parsed.detail;
      } catch(e) {}
      
      toast({ title: "Sign Up Failed", description: errorMsg, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-slate-50/50 to-blue-50/30 flex items-center justify-center p-4">
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
          <h1 className="text-3xl font-bold text-foreground">Join Metis</h1>
          <p className="text-muted-foreground mt-2">Create your secure account to get started</p>
        </div>

        {/* Signup Form */}
        <Card className="shadow-large border-0">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Create Account</CardTitle>
            <CardDescription>
              Start protecting your sensitive data with enterprise-grade security
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    placeholder="John"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange("firstName", e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    placeholder="Doe"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange("lastName", e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Work Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="john.doe@company.com"
                  value={formData.email}
                  onChange={(e) => handleInputChange("email", e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="company">Company</Label>
                <Input
                  id="company"
                  placeholder="Your Company"
                  value={formData.company}
                  onChange={(e) => handleInputChange("company", e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={(e) => handleInputChange("password", e.target.value)}
                  required
                />
                {formData.password && (
                  <div className="text-xs space-y-1 mt-2">
                    <div className={`flex items-center ${isLengthValid ? "text-success" : "text-muted-foreground"}`}>
                      {isLengthValid ? "✓" : "○"} At least 8 characters
                    </div>
                    <div className={`flex items-center ${hasSpecialChar ? "text-success" : "text-muted-foreground"}`}>
                      {hasSpecialChar ? "✓" : "○"} At least 1 special character
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                  required
                />
                {formData.confirmPassword && (
                  <div className="text-xs mt-1">
                    {passwordsMatch ? (
                      <span className="text-success flex items-center">✓ Passwords match</span>
                    ) : (
                      <span className="text-destructive flex items-center">○ Passwords do not match</span>
                    )}
                  </div>
                )}
              </div>

              <Button 
                type="submit" 
                variant="security"
                className="w-full h-12" 
                disabled={isLoading || !isFormValid}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                    Creating Account...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Create Account
                  </div>
                )}
              </Button>
            </form>

            <Separator className="my-6" />

            <div className="text-center">
              <p className="text-sm text-muted-foreground">
                Already have an account?{" "}
                <button 
                  onClick={() => navigate("/login")}
                  className="text-primary hover:text-primary/80 font-medium"
                >
                  Sign in here
                </button>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Terms Notice */}
        <div className="mt-6 text-center text-xs text-muted-foreground">
          <p>
            By creating an account, you agree to our{" "}
            <a href="#" className="text-primary hover:underline">Terms of Service</a>
            {" "}and{" "}
            <a href="#" className="text-primary hover:underline">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignUp;