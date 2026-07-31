import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { AdminPage } from "./pages/AdminPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { InspectionsPage } from "./pages/InspectionsPage";
import { LoginPage } from "./pages/LoginPage";
import { SitesPage } from "./pages/SitesPage";
import { StatusPage } from "./pages/StatusPage";

export function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="sites" element={<SitesPage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="inspections" element={<InspectionsPage />} />
          <Route path="admin" element={<AdminPage />} />
          <Route path="status" element={<StatusPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
