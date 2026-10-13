import { BarChart3, BriefcaseBusiness, FileText, LayoutDashboard, Menu, ShieldCheck, SlidersHorizontal, TrendingUp, X } from 'lucide-react';
import { type ReactNode, useState } from 'react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'Verify Invoice', path: '/verify', icon: FileText },
  { label: 'Invoices', path: '/invoices', icon: BriefcaseBusiness },
  { label: 'Audit Trail', path: '/audit', icon: ShieldCheck },
  { label: 'Analytics', path: '/analytics', icon: TrendingUp },
  { label: 'Settings', path: '/settings', icon: SlidersHorizontal },
];

export function AppShell({ children }: { children: ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="app-shell">
      <div className="flex min-h-screen bg-surface">
        <aside className={`${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-navy text-white transition-transform duration-200 lg:static lg:translate-x-0`}>
          <div className="flex items-center justify-between border-b border-slate-700 px-5 py-5">
            <div>
              <div className="text-xl font-bold">InvoiceShield</div>
              <div className="text-xs text-slate-300">Financing verification</div>
            </div>
            <button
              type="button"
              className="rounded-lg border border-slate-600 p-2 text-slate-200 lg:hidden"
              onClick={() => setMobileMenuOpen(false)}
              aria-label="Close navigation"
            >
              <X size={18} />
            </button>
          </div>

          <nav className="flex-1 space-y-2 p-4">
            {navItems.map(({ label, path, icon: Icon }) => (
              <NavLink
                key={path}
                to={path}
                end={path === '/dashboard'}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="border-t border-slate-700 p-4 text-sm text-slate-300">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue/20 text-xs font-semibold text-blue">
                IS
              </div>
              <div>
                <div className="font-medium text-white">Ops Team</div>
                <div className="text-xs text-slate-300">Verification desk</div>
              </div>
            </div>
          </div>
        </aside>

        <div className="flex-1">
          <header className="border-b border-border bg-white/80 px-4 py-3 backdrop-blur sm:px-6">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  className="rounded-xl border border-border p-2 text-text lg:hidden"
                  onClick={() => setMobileMenuOpen(true)}
                  aria-label="Open navigation"
                >
                  <Menu size={18} />
                </button>
                <div>
                  <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Verification workflow</div>
                  <div className="text-sm text-slate-600">InvoiceShield workspace</div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="hidden rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-slate-500 sm:block">
                  Demo mode enabled
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface font-semibold text-text">
                  IS
                </div>
              </div>
            </div>
          </header>

          <main className="p-4 sm:p-6 lg:p-8">{children}</main>
        </div>
      </div>

      {mobileMenuOpen && (
        <button
          type="button"
          aria-label="Close mobile nav overlay"
          className="fixed inset-0 z-30 bg-slate-950/30 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
    </div>
  );
}
