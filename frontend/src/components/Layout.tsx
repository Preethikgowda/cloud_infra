import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import PageContainer from './PageContainer';

const SIDEBAR_EXPANDED = 280;
const SIDEBAR_COLLAPSED = 80;

const Layout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [viewportWidth, setViewportWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      setViewportWidth(width);

      if (width < 768) {
        setCollapsed(false);
        setMobileOpen(false);
      } else if (width < 1280) {
        setCollapsed(true);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const sidebarWidth = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED;
  const contentOffset = viewportWidth >= 768 ? sidebarWidth : 0;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100">
      <Sidebar
        isOpen={mobileOpen}
        collapsed={collapsed}
        width={sidebarWidth}
        onToggle={() => setMobileOpen((value) => !value)}
        onCollapseToggle={() => setCollapsed((value) => !value)}
      />

      <div className="min-h-screen transition-all duration-300" style={{ marginLeft: contentOffset }}>
        <Navbar onMenuToggle={() => setMobileOpen((value) => !value)} />
        <PageContainer>
          <Outlet />
        </PageContainer>
      </div>
    </div>
  );
};

export default Layout;
