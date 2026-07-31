import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Keuringen</h1>
        <nav>
          <NavLink to="/" end>
            Dashboard
          </NavLink>
          <NavLink to="/sites">Sites</NavLink>
          <NavLink to="/documents">Documenten</NavLink>
          <NavLink to="/inspections">Keuringen</NavLink>
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
