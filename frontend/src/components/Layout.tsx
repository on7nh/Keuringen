import { NavLink, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { LanguageSwitcher } from "./LanguageSwitcher";

export function Layout() {
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();

  const needsStrongAuthSetup =
    !!user && user.strong_authentication_required && user.active_strong_auth_methods.length === 0;

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-brand">
          <img
            src="/logo.png"
            alt=""
            className="app-logo"
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
          <h1>Keuringen</h1>
        </div>
        <nav>
          <NavLink to="/" end>
            {t("nav.dashboard")}
          </NavLink>
          <NavLink to="/sites">{t("nav.sites")}</NavLink>
          <NavLink to="/documents">{t("nav.documents")}</NavLink>
          <NavLink to="/inspections">{t("nav.inspections")}</NavLink>
          {user?.is_system_admin && <NavLink to="/admin">{t("nav.admin")}</NavLink>}
          {user?.is_system_admin && <NavLink to="/status">{t("nav.status")}</NavLink>}
        </nav>
        <div className="app-header-user">
          <LanguageSwitcher />
          <NavLink to="/security">{user?.display_name}</NavLink>
          <button type="button" onClick={() => void logout()}>
            {t("nav.logout")}
          </button>
        </div>
      </header>
      <main className="app-content">
        {needsStrongAuthSetup && location.pathname !== "/security" && (
          <div className="setup-banner" role="alert">
            <span>{t("setupBanner.message")}</span>
            <NavLink to="/security" className="link-button">
              {t("setupBanner.action")}
            </NavLink>
          </div>
        )}
        <Outlet />
      </main>
    </div>
  );
}
