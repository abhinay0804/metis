import { useState, useEffect } from "react";
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
import { apiGetMe, apiUpdateMe, apiUpdatePhoto, apiStats, apiHistory } from "@/lib/api";
import { formatDistanceToNow, format } from "date-fns";

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState({
    name: "",
    email: "",
    phone: "",
    company: "",
    role: "",
    department: "",
    country: "",
    created_at: "",
    photo_base64: ""
  });
  const [stats, setStats] = useState<any>(null);
  const [activity, setActivity] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState("general");
  const { toast } = useToast();

  useEffect(() => {
    (window as any).isProfileEditing = isEditing;
    
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isEditing) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      (window as any).isProfileEditing = false;
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isEditing]);

  const handleTabChange = (value: string) => {
    if (isEditing) {
      if (window.confirm("You have unsaved changes. Do you want to discard them and switch tabs?")) {
        setIsEditing(false);
        setActiveTab(value);
      }
    } else {
      setActiveTab(value);
    }
  };

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 2 * 1024 * 1024) {
        toast({ title: "Image too large", description: "Please upload an image smaller than 2MB.", variant: "destructive" });
        return;
      }
      const reader = new FileReader();
      reader.onload = async (event) => {
        const base64 = event.target?.result as string;
        try {
          await apiUpdatePhoto(base64);
          setProfile(prev => ({ ...prev, photo_base64: base64 }));
          toast({ title: "Photo updated successfully!" });
        } catch (error: any) {
          toast({ title: "Failed to update photo", description: error.message, variant: "destructive" });
        }
      };
      reader.readAsDataURL(file);
    }
  };

  useEffect(() => {
    Promise.all([apiGetMe(), apiStats(), apiHistory()])
      .then(([userData, statsData, historyData]) => {
        setProfile({
          name: userData.full_name || "",
          email: userData.email || "",
          phone: userData.phone || "",
          company: userData.company || "",
          role: userData.role || "User",
          department: userData.department || "",
          country: userData.country || "",
          created_at: userData.created_at || "",
          photo_base64: userData.photo_base64 || ""
        });
        setStats(statsData);
        setActivity(historyData.slice(0, 5));
      })
      .catch(err => console.error("Failed to fetch profile data", err));
  }, []);

  const handleSave = async () => {
    if (profile.phone && profile.phone.length !== 10) {
      toast({
        title: "Invalid Phone Number",
        description: "Phone number must be exactly 10 digits.",
        variant: "destructive"
      });
      return;
    }
    try {
      await apiUpdateMe({
        full_name: profile.name,
        phone: profile.phone,
        company: profile.company,
        department: profile.department,
        country: profile.country
      });
      setIsEditing(false);
      toast({
        title: "Profile Updated",
        description: "Your profile information has been saved successfully.",
      });
    } catch (err: any) {
      toast({
        title: "Update Failed",
        description: "Could not save profile changes.",
        variant: "destructive"
      });
    }
  };

  const securitySettings = [
    { label: "Two-Factor Authentication", enabled: true, description: "Secure your account with 2FA" },
    { label: "Email Notifications", enabled: true, description: "Receive security alerts via email" },
    { label: "API Access", enabled: false, description: "Enable API access for integrations" },
    { label: "Session Timeout", enabled: true, description: "Auto-logout after 30 minutes" },
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

        <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
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
                        <AvatarImage src={profile.photo_base64 || ""} className="object-cover" />
                        <AvatarFallback className="text-lg font-semibold bg-primary text-primary-foreground">
                          {(profile.name || profile.email || "U").split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex flex-col space-y-1">
                        <h3 className="font-medium text-lg">{profile.name}</h3>
                        <p className="text-sm text-muted-foreground">{profile.role}</p>
                        <div className="pt-2 flex items-center space-x-2">
                          <Input type="file" id="photo-upload" className="hidden" accept="image/*" onChange={handlePhotoUpload} />
                          <Button variant="ghost" size="sm" className="h-8 px-2 text-xs" asChild>
                            <label htmlFor="photo-upload" className="cursor-pointer">
                              <Camera className="mr-2 h-3 w-3" />
                              Change Photo
                            </label>
                          </Button>
                        </div>
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
                          readOnly={true}
                          disabled={true}
                          className="bg-muted"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="phone">Phone</Label>
                        <Input
                          id="phone"
                          value={profile.phone}
                          onChange={(e) => setProfile({...profile, phone: e.target.value.replace(/\D/g, '').slice(0, 10)})}
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
                          readOnly={true}
                          disabled={true}
                          className="bg-muted"
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
                      <div className="space-y-2">
                        <Label htmlFor="country">Country</Label>
                        <select
                          id="country"
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                          value={profile.country}
                          onChange={(e) => setProfile({...profile, country: e.target.value})}
                          disabled={!isEditing}
                        >
                          <option value="">Select a country</option>
                          <option value="United States">United States</option>
                          <option value="United Kingdom">United Kingdom</option>
                          <option value="India">India</option>
                          <option value="Canada">Canada</option>
                          <option value="Australia">Australia</option>
                          <option value="Germany">Germany</option>
                          <option value="France">France</option>
                          <option value="Japan">Japan</option>
                        </select>
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
                      <Badge variant="default">General</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Member Since</span>
                      <span className="text-sm font-medium">
                        {profile.created_at ? format(new Date(profile.created_at), 'MMM yyyy') : "N/A"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Files Processed</span>
                      <span className="text-sm font-medium">{stats?.total_jobs || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Entities Masked</span>
                      <span className="text-sm font-medium">{stats?.total_pii_detections || 0}</span>
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
                  {activity.length > 0 ? activity.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{item.job_type === 'analysis' ? 'Analysis completed' : 'File masked'}</h4>
                        <p className="text-sm text-muted-foreground">
                          {item.file_name}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">
                          {item.created_at ? formatDistanceToNow(new Date(item.created_at), { addSuffix: true }) : ''}
                        </p>
                        <Badge 
                          variant={item.status === 'completed' ? 'default' : 'secondary'}
                          className="mt-1"
                        >
                          {item.status}
                        </Badge>
                      </div>
                    </div>
                  )) : (
                    <p className="text-sm text-muted-foreground">No recent activity.</p>
                  )}
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