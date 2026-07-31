import { useEffect, useState } from "react";

import { apiRequest } from "../api/client";
import type { SystemStatus } from "../api/types";

const STATUS_LABEL: Record<string, string> = {
  ok: "OK",
  error: "Fout",
  not_configured: "Niet geconfigureerd",
  unknown: "Onbekend",
  update_available: "Update beschikbaar",
};

export function StatusPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  async function load() {
    try {
      const result = await apiRequest<SystemStatus>("/system/status");
      setStatus(result);
      setLastChecked(new Date());
      setError(null);
    } catch {
      setError("Kon systeemstatus niet ophalen.");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div>
      <h2>Systeemstatus</h2>
      {error && <p className="error">{error}</p>}
      <button type="button" onClick={() => void load()}>
        Vernieuwen
      </button>
      {lastChecked && <p className="hint">Laatst gecontroleerd: {lastChecked.toLocaleTimeString()}</p>}

      {status && (
        <table>
          <thead>
            <tr>
              <th>Component</th>
              <th>Status</th>
              <th>Details</th>
              <th>Latentie</th>
            </tr>
          </thead>
          <tbody>
            {status.checks.map((check) => (
              <tr key={check.name}>
                <td>{check.label}</td>
                <td>
                  <span className={`status-badge status-${check.status}`}>
                    {STATUS_LABEL[check.status] ?? check.status}
                  </span>
                </td>
                <td>{check.detail ?? "-"}</td>
                <td>{check.latency_ms !== null ? `${check.latency_ms} ms` : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
