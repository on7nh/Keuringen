import { useEffect, useState } from "react";

import { apiRequest } from "../api/client";

interface InspectionSchedule {
  id: string;
  site_id: string;
  next_due_date: string;
  status: string;
}

export function DashboardPage() {
  const [due, setDue] = useState<InspectionSchedule[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<InspectionSchedule[]>("/inspections/due?within_days=90")
      .then(setDue)
      .catch(() => setError("Kon vervaldata niet laden."));
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <section>
        <h3>Keuringen die binnen 90 dagen vervallen</h3>
        {error && <p className="error">{error}</p>}
        {due === null && !error && <p>Laden...</p>}
        {due && due.length === 0 && <p>Geen keuringen vervallen binnenkort.</p>}
        {due && due.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Site</th>
                <th>Vervaldatum</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {due.map((item) => (
                <tr key={item.id}>
                  <td>{item.site_id}</td>
                  <td>{item.next_due_date}</td>
                  <td>{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
