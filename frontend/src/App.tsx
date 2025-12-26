import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { InstallPrompt } from '@/components/InstallPrompt';
import { TurnBudget } from '@/components/TurnBudget';
import { Suspense, lazy } from 'react';

// Lazy load pages
const LoginPage = lazy(() => import('./pages/LoginPage'));
const EnvelopesPage = lazy(() => import('./pages/EnvelopesPage'));
const ThreadPage = lazy(() => import('./pages/ThreadPage'));

function Layout() {
  return (
    <div className="flex flex-col h-screen bg-background text-foreground overflow-hidden">
      <header className="flex items-center justify-between p-4 border-b border-border bg-card/50 backdrop-blur-sm relative z-20">
        <h1 className="text-xl font-bold tracking-tighter">Slowburn</h1>
        <TurnBudget />
      </header>

      <main className="flex-1 overflow-y-auto relative z-10">
        <Suspense fallback={<div className="p-8 text-center text-muted-foreground">Loading...</div>}>
          <Outlet />
        </Suspense>
      </main>

      <InstallPrompt />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/envelopes" replace />} />
          <Route path="/envelopes" element={<EnvelopesPage />} />
          <Route path="/threads/:id" element={<ThreadPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
