import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import { AuthProvider } from "@/hooks/useAuth";
import { ThemeProvider } from "@/hooks/useTheme";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { ARIAProvider } from "@/contexts/ARIAContext";
import { ActiveBusinessProvider } from "@/contexts/ActiveBusinessContext";
import { ARIADrawer } from "@/components/aria/ARIADrawer";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Clients from "./pages/Clients";
import Content from "./pages/Content";
import ContentLabPageV2 from "./pages/ContentLabPageV2";
import Strategies from "./pages/Strategies";
import CalendarPage from "./pages/Calendar";
import Media from "./pages/Media";
import Analytics from "./pages/Analytics";
import IntelligencePage from "./pages/IntelligencePage";
import BrandVoicePage from "./pages/BrandVoicePage";
import CrisisPage from "./pages/CrisisPage";
import AddOnsPage from "./pages/AddOnsPage";
import SecurityDevPage from "./pages/SecurityDevPage";
import SettingsPage from "./pages/SettingsPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Switcher V1: /clients/:id legado → /clients?business=:id (preserva bookmarks viejos).
function ClientLegacyRedirect() {
  const { id } = useParams<{ id: string }>();
  return <Navigate to={`/clients?business=${id}`} replace />;
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <AuthProvider>
        <ARIAProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <ARIADrawer />
            <BrowserRouter>
            <ActiveBusinessProvider>
            <Routes>
              <Route path="/auth" element={<Auth />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <AppLayout><Dashboard /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/clients"
                element={
                  <ProtectedRoute>
                    <AppLayout><Clients /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/clients/:id"
                element={
                  <ProtectedRoute>
                    <ClientLegacyRedirect />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/content-lab"
                element={
                  <ProtectedRoute>
                    <AppLayout><ContentLabPageV2 /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/estrategias"
                element={
                  <ProtectedRoute>
                    <AppLayout><Strategies /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/content"
                element={
                  <ProtectedRoute>
                    <AppLayout><Content /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/calendar"
                element={
                  <ProtectedRoute>
                    <AppLayout><CalendarPage /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/media"
                element={
                  <ProtectedRoute>
                    <AppLayout><Media /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/analytics"
                element={
                  <ProtectedRoute>
                    <AppLayout><Analytics /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/intelligence"
                element={
                  <ProtectedRoute>
                    <AppLayout><IntelligencePage /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/brand-voice"
                element={
                  <ProtectedRoute>
                    <AppLayout><BrandVoicePage /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/crisis"
                element={
                  <ProtectedRoute>
                    <AppLayout><CrisisPage /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/add-ons"
                element={
                  <ProtectedRoute>
                    <AppLayout><AddOnsPage /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/security-dev"
                element={
                  <ProtectedRoute>
                    <AppLayout><SecurityDevPage /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/settings"
                element={
                  <ProtectedRoute>
                    <AppLayout><SettingsPage /></AppLayout>
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<NotFound />} />
            </Routes>
            </ActiveBusinessProvider>
            </BrowserRouter>
          </TooltipProvider>
        </ARIAProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
