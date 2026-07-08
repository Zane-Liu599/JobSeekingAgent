import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import {
  FaClipboardCheck,
  FaFileAlt,
  FaHome,
  FaPlusCircle,
  FaSearch,
  FaUserEdit,
  FaWarehouse
} from "react-icons/fa";

import { AddLeadPage } from "../pages/AddLeadPage";
import { ApplicationTrackerPage } from "../pages/ApplicationTrackerPage";
import { DashboardPage } from "../pages/DashboardPage";
import { JobSearchPage } from "../pages/JobSearchPage";
import { MaterialsPage } from "../pages/MaterialsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { SavedJobsPage } from "../pages/SavedJobsPage";

const navItems = [
  { to: "/", label: "Overview", icon: <FaHome /> },
  { to: "/search", label: "Find Jobs", icon: <FaSearch /> },
  { to: "/jobs", label: "Saved Jobs", icon: <FaWarehouse /> },
  { to: "/materials", label: "Materials", icon: <FaFileAlt /> },
  { to: "/tracker", label: "Tracker", icon: <FaClipboardCheck /> },
  { to: "/profile", label: "Profile", icon: <FaUserEdit /> },
  { to: "/add-lead", label: "Add Lead", icon: <FaPlusCircle /> }
];

export function AppRouter() {
  return (
    <BrowserRouter>
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
        </aside>
        <main className="content">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/search" element={<JobSearchPage />} />
            <Route path="/jobs" element={<SavedJobsPage />} />
            <Route path="/materials" element={<MaterialsPage />} />
            <Route path="/tracker" element={<ApplicationTrackerPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/add-lead" element={<AddLeadPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
