import React from 'react';
import { useAuth } from '../auth/AuthContext';

interface NavbarProps {
  onMenuToggle: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onMenuToggle }) => {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-30 border-b border-slate-800/90 bg-[#020617]/90 backdrop-blur">
      <div className="mx-auto flex h-16 w-full max-w-[1600px] items-center justify-between px-4 md:px-6 xl:px-10">
        <button onClick={onMenuToggle} className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-300 md:hidden">
          Menu
        </button>
        <div className="hidden text-sm text-slate-400 md:block">IntelliWealth workspace</div>
        <div className="flex items-center gap-3 text-sm text-slate-300">
          <span className="hidden sm:inline capitalize">{user?.role}</span>
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 font-semibold text-white">
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
