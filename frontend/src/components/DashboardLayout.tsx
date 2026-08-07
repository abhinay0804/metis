import { useState, useEffect } from "react";
import { apiGetMe } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  LayoutDashboard, 
  Shield, 
  User, 
  Settings, 
  LogOut, 
  Menu,
  BarChart3,
  History,
  Bell
} from "lucide-react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { ModeToggle } from "./mode-toggle";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userData, setUserData] = useState({ name: "Loading...", email: "", initials: "U" });
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  useEffect(() => {
    apiGetMe()
      .then(data => {
        const name = data.full_name || data.email?.split('@')[0] || "User";
        const email = data.email || "";
        const initials = name.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase();
        setUserData({ name, email, initials });
      })
      .catch(console.error);
  }, []);

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "History", href: "/history", icon: History },
    { name: "Profile", href: "/profile", icon: User },
  ];

  const handleLogout = () => {
    localStorage.removeItem('idToken');
    window.location.href = "/";
  };

  const handleLogoClick = () => {
    if ((window as any).isProfileEditing) {
      if (!window.confirm("You have unsaved changes. Are you sure you want to discard them and leave?")) {
        return;
      }
    }
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-card shadow-soft">
        <div className="flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </Button>
            
            <div 
              className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={handleLogoClick}
            >
              <div className="flex h-8 w-8 items-center justify-center bg-primary rounded-lg">
                <Shield className="h-5 w-5 text-primary-foreground" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold">Metis</h1>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <ModeToggle />
            <Button 
              variant="ghost" 
              size="icon" 
              className="relative text-muted-foreground hover:text-foreground"
              onClick={() => toast({ title: "No new notifications", description: "You're all caught up!" })}
            >
              <Bell className="h-5 w-5" />
              <span className="absolute top-2 right-2 h-2 w-2 bg-destructive rounded-full border-2 border-background"></span>
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="" alt="Avatar" />
                    <AvatarFallback className="bg-primary text-primary-foreground">{userData.initials}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{userData.name}</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {userData.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuItem onClick={(e) => {
                  if ((window as any).isProfileEditing && !window.confirm("You have unsaved changes. Are you sure you want to discard them and leave?")) {
                    e.preventDefault();
                    return;
                  }
                  navigate("/profile");
                }}>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={(e) => {
                  if ((window as any).isProfileEditing && !window.confirm("You have unsaved changes. Are you sure you want to discard them and leave?")) {
                    e.preventDefault();
                    return;
                  }
                  navigate("/profile");
                }}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={(e) => {
                  if ((window as any).isProfileEditing && !window.confirm("You have unsaved changes. Are you sure you want to discard them and leave?")) {
                    e.preventDefault();
                    return;
                  }
                  handleLogout();
                }}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside 
          className={cn(
            "fixed inset-y-0 left-0 z-40 w-64 transform border-r bg-card shadow-soft transition-transform duration-200 ease-in-out lg:relative lg:translate-x-0",
            sidebarOpen ? "translate-x-0" : "-translate-x-full lg:w-16"
          )}
        >
          <div className="flex h-full flex-col pt-16 lg:pt-0">
            <nav className="flex-1 space-y-1 px-3 py-4">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;
                
                return (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    onClick={(e) => {
                      if ((window as any).isProfileEditing && !window.confirm("You have unsaved changes. Are you sure you want to discard them and leave?")) {
                        e.preventDefault();
                      }
                    }}
                    className={cn(
                      "group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                  >
                    <Icon 
                      className={cn(
                        "mr-3 h-5 w-5 flex-shrink-0",
                        !sidebarOpen && "lg:mr-0"
                      )} 
                    />
                    <span className={cn(!sidebarOpen && "lg:hidden")}>
                      {item.name}
                    </span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        </aside>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 z-30 bg-black bg-opacity-50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main content */}
        <main className="flex-1 min-w-0">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;