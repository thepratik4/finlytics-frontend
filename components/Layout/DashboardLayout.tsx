import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { BarChart3, Upload, FileText, MessageSquare, LogOut, Menu, X } from 'lucide-react';
import { Button, cn } from '../ui/Primitives';

export default function DashboardLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/dashboard/upload', icon: Upload, label: 'Upload' },
    { to: '/dashboard/results', icon: BarChart3, label: 'Analysis Results' },
    { to: '/dashboard/qa', icon: MessageSquare, label: 'Q & A' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Mobile Header */}
      <header className="md:hidden bg-white border-b border-gray-200 p-4 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <BarChart3 className="text-white h-5 w-5" />
          </div>
          <span className="font-bold text-lg text-slate-800">Finlytics</span>
        </div>
        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 text-slate-600">
          {isSidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </header>

      {/* Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={cn(
        "fixed md:sticky top-0 left-0 z-50 h-screen w-64 bg-slate-900 text-white transform transition-transform duration-200 ease-in-out md:translate-x-0 flex flex-col",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 bg-primary-500 rounded-lg flex items-center justify-center">
              <BarChart3 className="text-white h-5 w-5" />
            </div>
            <span className="font-bold text-xl">Finlytics</span>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setIsSidebarOpen(false)}
              className={({ isActive }) => cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive 
                  ? "bg-primary-600 text-white" 
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 px-3 py-3 mb-2">
            <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-medium">
              {user?.email?.[0].toUpperCase()}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium truncate">{user?.email}</p>
              <p className="text-xs text-slate-400">Pro Plan</p>
            </div>
          </div>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-slate-800"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 min-w-0 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-4 md:p-8">
           <Outlet />
        </div>
      </main>
    </div>
  );
}