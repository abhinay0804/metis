import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  User, 
  Mail, 
  Phone, 
  Building, 
  Shield, 
  Key, 
  Bell, 
  Save,
  Camera,
  Download,
  Activity
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import DashboardLayout from "@/components/DashboardLayout";

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState({
    name: "Sarah Wilson",
    email: "sarah.wilson@company.com",
    phone: "+1 (555) 123-4567",
    company: "SecureData Corp",
    role: "Data Privacy Officer",
    department: "Information Security"
  });
  const { toast } = useToast();

  const handleSave = () => {
    setIsEditing(false);
    toast({
      title: "Profile Updated",
      description: "Your profile information has been saved successfully.",
    });
  };

  const securitySettings = [
    { label: "Two-Factor Authentication", enabled: true, description: "Secure your account with 2FA" },
    { label: "Email Notifications", enabled: true, description: "Receive security alerts via email" },
    { label: "API Access", enabled: false, description: "Enable API access for integrations" },
    { label: "Session Timeout", enabled: true, description: "Auto-logout after 30 minutes" },
  ];

  const activityLog = [
    { action: "File masked", file: "customer_data.csv", time: "2 hours ago", status: "success" },
    { action: "Analysis completed", file: "transaction_log.xlsx", time: "5 hours ago", status: "success" },
    { action: "Login", location: "New York, US", time: "1 day ago", status: "info" },
    { action: "Export report", file: "compliance_report.pdf", time: "2 days ago", status: "success" },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Profile</h1>
          <p className="text-muted-foreground">
            Manage your account settings and security preferences
          </p>
        </div>

        <Tabs defaultValue="general" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
          </TabsList>

          {/* General Tab */}
          <TabsContent value="general" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Profile Info */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Profile Information</CardTitle>
                        <CardDescription>
                          Update your personal and professional details
                        </CardDescription>
                      </div>
                      <Button
                        variant={isEditing ? "default" : "outline"}
                        onClick={() => isEditing ? handleSave() : setIsEditing(true)}
                      >
                        {isEditing ? (
                          <><Save className="h-4 w-4 mr-2" /> Save</>
                        ) : (
                          <><User className="h-4 w-4 mr-2" /> Edit</>
                        )}
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center space-x-4">
                      <Avatar className="h-20 w-20">
                        <AvatarImage src="/placeholder-avatar.jpg" />
                        <AvatarFallback className="text-lg font-semibold bg-primary text-primary-foreground">
                          SW
                        </AvatarFallback>
                      </Avatar>
                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold">{profile.name}</h3>
                        <p className="text-sm text-muted-foreground">{profile.role}</p>
                        <Button variant="ghost" size="sm" className="h-8">
                          <Camera className="h-4 w-4 mr-2" />
                          Change Photo
                        </Button>
                      </div>
                    </div>

                    <Separator />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="name">Full Name</Label>
                        <Input
                          id="name"
                          value={profile.name}
                          onChange={(e) => setProfile({...profile, name: e.target.value})}
                          disabled={!isEditing}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email">Email</Label>
                        <Input
                          id="email"
                          type="email"
                          value={profile.email}
                          onChange={(e) => setProfile({...profile, email: e.target.value})}
                          disabled={!isEditing}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="phone">Phone</Label>
                        <Input
                          id="phone"
                          value={profile.phone}
                          onChange={(e) => setProfile({...profile, phone: e.target.value})}
                          disabled={!isEditing}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="company">Company</Label>
                        <Input
                          id="company"
                          value={profile.company}
                          onChange={(e) => setProfile({...profile, company: e.target.value})}
                          disabled={!isEditing}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="role">Role</Label>
                        <Input
                          id="role"
                          value={profile.role}
                          onChange={(e) => setProfile({...profile, role: e.target.value})}
                          disabled={!isEditing}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="department">Department</Label>
                        <Input
                          id="department"
                          value={profile.department}
                          onChange={(e) => setProfile({...profile, department: e.target.value})}
                          disabled={!isEditing}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Account Stats */}
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Account Status</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Account Type</span>
                      <Badge variant="default">Premium</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Member Since</span>
                      <span className="text-sm font-medium">Jan 2024</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Files Processed</span>
                      <span className="text-sm font-medium">1,247</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Data Masked</span>
                      <span className="text-sm font-medium">2.3 GB</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Security Settings
                </CardTitle>
                <CardDescription>
                  Configure security preferences and access controls
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {securitySettings.map((setting, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">{setting.label}</h4>
                      <p className="text-sm text-muted-foreground">{setting.description}</p>
                    </div>
                    <Badge variant={setting.enabled ? "default" : "secondary"}>
                      {setting.enabled ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>
                ))}
                
                <Separator />
                
                <div className="space-y-4">
                  <h4 className="font-medium flex items-center gap-2">
                    <Key className="h-4 w-4" />
                    Password & Authentication
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Button variant="outline">Change Password</Button>
                    <Button variant="outline">Setup 2FA</Button>
                    <Button variant="outline">Generate API Key</Button>
                    <Button variant="outline">Download Backup Codes</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Notification Preferences
                </CardTitle>
                <CardDescription>
                  Manage how you receive updates and alerts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  {[
                    "Processing completed notifications",
                    "Security alerts",
                    "System maintenance updates", 
                    "Weekly summary reports",
                    "Compliance alerts"
                  ].map((notification, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <span className="font-medium">{notification}</span>
                      <Badge variant="default">Email</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Activity Tab */}
          <TabsContent value="activity" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Recent Activity
                </CardTitle>
                <CardDescription>
                  Your recent actions and system events
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {activityLog.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{item.action}</h4>
                        <p className="text-sm text-muted-foreground">
                          {item.file || item.location}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">{item.time}</p>
                        <Badge 
                          variant={item.status === 'success' ? 'default' : 'secondary'}
                          className="mt-1"
                        >
                          {item.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

export default Profile;