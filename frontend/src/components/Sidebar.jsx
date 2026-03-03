import { MessageSquare, FileUp, Settings, LogOut } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function Sidebar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { path: '/chat', label: 'Chat', icon: MessageSquare },
    { path: '/documents', label: 'Documents', icon: FileUp },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-blue-600">SRAG</h1>
        <p className="text-xs text-gray-500 mt-1">RAG Chat</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map(({ path, label, icon: Icon }) => (
          <Link
            key={path}
            to={path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
              isActive(path)
                ? 'bg-blue-50 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Icon className="w-5 h-5" />
            {label}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <button className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:text-red-600 text-sm font-medium w-full">
          <LogOut className="w-4 h-4" />
          Quit
        </button>
        <p className="text-xs text-gray-400 mt-4 text-center">v0.2.0</p>
      </div>
    </div>
  );
}
