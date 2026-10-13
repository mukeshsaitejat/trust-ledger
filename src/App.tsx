import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import AnalyticsPage from './pages/AnalyticsPage';
import AuditTrailPage from './pages/AuditTrailPage';
import DashboardPage from './pages/DashboardPage';
import InvoiceDetailPage from './pages/InvoiceDetailPage';
import InvoicesPage from './pages/InvoicesPage';
import SettingsPage from './pages/SettingsPage';
import VerifyInvoicePage from './pages/VerifyInvoicePage';

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/verify" element={<VerifyInvoicePage />} />
        <Route path="/invoices" element={<InvoicesPage />} />
        <Route path="/invoices/:invoiceId" element={<InvoiceDetailPage />} />
        <Route path="/audit" element={<AuditTrailPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </AppShell>
  );
}
