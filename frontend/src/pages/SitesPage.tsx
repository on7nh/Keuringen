import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { ApiError, apiRequest } from "../api/client";
import type { Organization, Site } from "../api/types";

export function SitesPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [orgId, setOrgId] = useState("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [siteNumber, setSiteNumber] = useState("");

  async function loadData() {
    try {
      const [orgs, siteList] = await Promise.all([
        apiRequest<Organization[]>("/organizations"),
        apiRequest<Site[]>("/sites"),
      ]);
      setOrganizations(orgs);
      setSites(siteList);
      if (orgs.length > 0) setOrgId((current) => current || orgs[0].id);
    } catch {
      setError("Kon organisaties/sites niet laden.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleCreateSite(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await apiRequest("/sites", {
        method: "POST",
        body: {
          organization_id: orgId,
          code,
          name,
          site_number: siteNumber || null,
        },
      });
      setCode("");
      setName("");
      setSiteNumber("");
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Aanmaken van Site mislukt.");
    }
  }

  return (
    <div>
      <h2>Sites</h2>
      {error && <p className="error">{error}</p>}

      <table>
        <thead>
          <tr>
            <th>Site</th>
            <th>Sitenummer</th>
            <th>Opslagcode</th>
            <th>Actief</th>
          </tr>
        </thead>
        <tbody>
          {sites.map((site) => (
            <tr key={site.id}>
              <td>
                {site.name} ({site.code})
              </td>
              <td>
                {site.site_number}
                {site.is_temporary_site_number ? " (tijdelijk)" : ""}
              </td>
              <td>{site.storage_code}</td>
              <td>{site.is_active ? "Ja" : "Nee"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Nieuwe Site</h3>
      <form onSubmit={handleCreateSite}>
        <label>
          Organisatie
          <select value={orgId} onChange={(e) => setOrgId(e.target.value)} required>
            {organizations.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Code
          <input value={code} onChange={(e) => setCode(e.target.value)} required />
        </label>
        <label>
          Naam
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Sitenummer (leeg = tijdelijk TMP-nummer)
          <input value={siteNumber} onChange={(e) => setSiteNumber(e.target.value)} />
        </label>
        <button type="submit">Site aanmaken</button>
      </form>
    </div>
  );
}
