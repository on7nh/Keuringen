import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { ApiError, apiRequest } from "../api/client";
import type { InspectionReport, InspectionStatus } from "../api/types";

const UNCONFIRMED_LABEL = "-------------";

export function InspectionsPage() {
  const [inspections, setInspections] = useState<InspectionReport[]>([]);
  const [statuses, setStatuses] = useState<InspectionStatus[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [statusId, setStatusId] = useState("");
  const [inspectionDate, setInspectionDate] = useState("");

  async function loadData() {
    try {
      const [inspectionList, statusList] = await Promise.all([
        apiRequest<InspectionReport[]>("/inspections"),
        apiRequest<InspectionStatus[]>("/inspection-statuses"),
      ]);
      setInspections(inspectionList);
      setStatuses(statusList);
    } catch {
      setError("Kon keuringen niet laden.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  function statusLabel(id: string): string {
    return statuses.find((s) => s.id === id)?.label ?? UNCONFIRMED_LABEL;
  }

  function selectForValidation(inspection: InspectionReport) {
    setSelectedId(inspection.id);
    setStatusId(inspection.inspection_status_id);
    setInspectionDate(inspection.inspection_date ?? new Date().toISOString().slice(0, 10));
    setMessage(null);
    setError(null);
  }

  async function handleValidate(e: FormEvent) {
    e.preventDefault();
    if (!selectedId) return;
    setError(null);
    setMessage(null);
    try {
      await apiRequest(`/inspections/${selectedId}/validate`, {
        method: "POST",
        body: { inspection_status_id: statusId, inspection_date: inspectionDate },
      });
      setMessage("Keuring bevestigd.");
      setSelectedId(null);
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Bevestigen mislukt.");
    }
  }

  return (
    <div>
      <h2>Keuringen</h2>
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      <table>
        <thead>
          <tr>
            <th>Keuringsdatum</th>
            <th>Vervaldatum</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {inspections.map((inspection) => (
            <tr key={inspection.id}>
              <td>{inspection.inspection_date ?? "-"}</td>
              <td>{inspection.expiry_date ?? "-"}</td>
              <td>{statusLabel(inspection.inspection_status_id)}</td>
              <td>
                <button type="button" onClick={() => selectForValidation(inspection)}>
                  Controleren
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedId && (
        <>
          <h3>Keuring bevestigen</h3>
          <form onSubmit={handleValidate}>
            <label>
              Keuringsstatus
              <select value={statusId} onChange={(e) => setStatusId(e.target.value)} required>
                {statuses.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Datum van onderzoek
              <input
                type="date"
                value={inspectionDate}
                onChange={(e) => setInspectionDate(e.target.value)}
                required
              />
            </label>
            <button type="submit">Bevestigen</button>
            <button type="button" className="link-button" onClick={() => setSelectedId(null)}>
              Annuleren
            </button>
          </form>
        </>
      )}
    </div>
  );
}
