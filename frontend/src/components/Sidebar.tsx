import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const navItems = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Portfolio', path: '/portfolio' },
  { label: 'Allocation', path: '/allocation' },
  { label: 'History', path: '/history' },
  { label: 'Profile', path: '/profile' },
];

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  collapsed: boolean;
  onCollapseToggle: () => void;
  width: number;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle, collapsed, onCollapseToggle, width }) => {
  const { user, logout } = useAuth();
  const items = user?.role === 'admin' ? [...navItems, { label: 'Admin', path: '/admin' }] : navItems;

  return (
    <>
      {isOpen && <button className="fixed inset-0 z-40 bg-black/60 md:hidden" onClick={onToggle} aria-label="Close menu" />}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex h-screen flex-col border-r border-slate-800 bg-[#0b1222] transition-transform duration-300 md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width }}
      >
        <div className="flex h-20 items-center border-b border-slate-800 px-6">
          <div className="mr-3 h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500" />
          {!collapsed && (
            <div>
              <p className="text-sm font-semibold text-slate-100">IntelliWealth</p>
              <p className="text-xs text-slate-400">Enterprise Suite</p>
            </div>
          )}
        </div>

        <nav className={`flex-1 space-y-2 overflow-y-auto py-8 ${collapsed ? 'px-3' : 'px-4'}`}>
          {items.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => window.innerWidth < 768 && onToggle()}
              className={({ isActive }) =>
                `flex h-11 items-center rounded-xl text-sm font-medium transition ${
                  collapsed ? 'justify-center px-2' : 'px-4'
                } ${isActive ? 'bg-gradient-to-r from-indigo-500/20 to-violet-500/20 text-indigo-200' : 'text-slate-300 hover:bg-slate-800/70 hover:text-slate-100'}`
              }
            >
              {collapsed ? item.label.charAt(0) : item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-slate-800 p-4">
          {!collapsed && <p className="mb-3 truncate text-sm text-slate-300">{user?.name}</p>}
          <div className="flex gap-2">
            <button
              onClick={onCollapseToggle}
              className="hidden h-10 flex-1 rounded-xl border border-slate-700 text-xs text-slate-300 transition hover:bg-slate-800 xl:block"
            >
              {collapsed ? 'Expand' : 'Collapse'}
            </button>
            <button
              onClick={logout}
              className="h-10 flex-1 rounded-xl border border-slate-700 text-xs text-slate-300 transition hover:bg-slate-800"
            >
              Logout
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;

