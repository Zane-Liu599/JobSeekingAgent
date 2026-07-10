import { BrowserRouter, Navigate, NavLink, Route, Routes, useNavigate } from "react-router-dom";
import {
  FaClipboardCheck,
  FaFileAlt,
  FaHome,
  FaPlusCircle,
  FaSearch,
  FaSignOutAlt,
  FaUserEdit,
  FaWarehouse
} from "react-icons/fa";

import { clearAuth, getAuthToken } from "../api/auth";
import { AddLeadPage } from "../pages/AddLeadPage";
import { ApplicationTrackerPage } from "../pages/ApplicationTrackerPage";
import { DashboardPage } from "../pages/DashboardPage";
import { JobSearchPage } from "../pages/JobSearchPage";
import { LandingPage } from "../pages/LandingPage";
import { LoginPage } from "../pages/LoginPage";
import { MaterialsPage } from "../pages/MaterialsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ProfileSetupPage } from "../pages/ProfileSetupPage";
import { RegisterPage } from "../pages/RegisterPage";
import { SavedJobsPage } from "../pages/SavedJobsPage";
import { VerifyEmailPage } from "../pages/VerifyEmailPage";
import { VerifyPendingPage } from "../pages/VerifyPendingPage";

const navItems = [
  { to: "/app", label: "Overview", icon: <FaHome /> },
  { to: "/app/search", label: "Find Jobs", icon: <FaSearch /> },
  { to: "/app/jobs", label: "Saved Jobs", icon: <FaWarehouse /> },
  { to: "/app/materials", label: "Materials", icon: <FaFileAlt /> },
  { to: "/app/tracker", label: "Tracker", icon: <FaClipboardCheck /> },
  { to: "/app/profile", label: "Profile", icon: <FaUserEdit /> },
  { to: "/app/add-lead", label: "Add Lead", icon: <FaPlusCircle /> }
];

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-pending" element={<VerifyPendingPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/app/*" element={<ProtectedApp />} />
        <Route path="/search" element={<Navigate to="/app/search" replace />} />
        <Route path="/jobs" element={<Navigate to="/app/jobs" replace />} />
        <Route path="/materials" element={<Navigate to="/app/materials" replace />} />
        <Route path="/tracker" element={<Navigate to="/app/tracker" replace />} />
        <Route path="/profile" element={<Navigate to="/app/profile" replace />} />
        <Route path="/profile-setup" element={<Navigate to="/app/profile-setup" replace />} />
        <Route path="/add-lead" element={<Navigate to="/app/add-lead" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

function ProtectedApp() {
  const navigate = useNavigate();
  const isAuthenticated = Boolean(getAuthToken());

  function handleLogout() {
    clearAuth();
    navigate("/login", { replace: true });
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            <span className="brand-mark">JSA</span>
            <span>JobSeekingAgent</span>
          </div>
          <nav className="nav flex-column gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                end={item.to === "/"}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </nav>
          <button className="logout-button" onClick={handleLogout} type="button">
            <FaSignOutAlt /> Log out
          </button>
        </aside>
        <main className="content">
          <Routes>
            <Route path="/app" element={<DashboardPage />} />
            <Route path="/app/profile-setup" element={<ProfileSetupPage />} />
            <Route path="/app/search" element={<JobSearchPage />} />
            <Route path="/app/jobs" element={<SavedJobsPage />} />
            <Route path="/app/materials" element={<MaterialsPage />} />
            <Route path="/app/tracker" element={<ApplicationTrackerPage />} />
            <Route path="/app/profile" element={<ProfilePage />} />
            <Route path="/app/add-lead" element={<AddLeadPage />} />
            <Route path="*" element={<Navigate to="/app/profile-setup" replace />} />
          </Routes>
        </main>
      </div>
  );
}
