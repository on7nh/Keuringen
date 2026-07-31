import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function Layout() {
  const { user, logout } = useAuth();

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
            Dashboard
          </NavLink>
          <NavLink to="/sites">Sites</NavLink>
          <NavLink to="/documents">Documenten</NavLink>
          <NavLink to="/inspections">Keuringen</NavLink>
          {user?.is_system_admin && <NavLink to="/admin">Beheer</NavLink>}
          {user?.is_system_admin && <NavLink to="/status">Systeemstatus</NavLink>}
        </nav>
        <div className="app-header-user">
          <span>{user?.display_name}</span>
          <button type="button" onClick={() => void logout()}>
            Afmelden
          </button>
        </div>
      </header>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}
