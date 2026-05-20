import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router";
import { useAuth } from "./context/AuthContext";
import AppLayout from "./layout/AppLayout";
import SignIn from "./pages/AuthPages/SignIn";
import DashboardPage from "./pages/DashboardPage";
import QuoteHistoryPage from "./pages/QuoteHistoryPage";
import SetupPage from "./pages/SetupPage";
import NotFound from "./pages/OtherPage/NotFound";
import { ScrollToTop } from "./components/common/ScrollToTop";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/signin" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Router>
      <ScrollToTop />
      <Routes>
        <Route path="/signin" element={<SignIn />} />

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index path="/" element={<DashboardPage />} />
          <Route path="/history" element={<QuoteHistoryPage />} />
          <Route path="/setup" element={<SetupPage />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}
