import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { ApiError, apiRequest } from "../api/client";
import type { Discipline, DocumentType, Organization } from "../api/types";

export function AdminPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [disciplines, setDisciplines] = useState<Discipline[]>([]);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [orgCode, setOrgCode] = useState("");
  const [orgName, setOrgName] = useState("");

  const [discCode, setDiscCode] = useState("");
  const [discName, setDiscName] = useState("");
  const [discValidityValue, setDiscValidityValue] = useState("");
  const [discValidityUnit, setDiscValidityUnit] = useState("year");

  const [typeCode, setTypeCode] = useState("");
  const [typeName, setTypeName] = useState("");
  const [typeRequiresInspection, setTypeRequiresInspection] = useState(false);

  async function loadData() {
    try {
      const [orgs, disciplineList, docTypeList] = await Promise.all([
        apiRequest<Organization[]>("/organizations"),
        apiRequest<Discipline[]>("/disciplines"),
        apiRequest<DocumentType[]>("/document-types"),
      ]);
      setOrganizations(orgs);
      setDisciplines(disciplineList);
      setDocumentTypes(docTypeList);
    } catch {
      setError("Kon beheergegevens niet laden.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleCreateOrganization(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      await apiRequest("/organizations", { method: "POST", body: { code: orgCode, name: orgName } });
      setOrgCode("");
      setOrgName("");
      setMessage("Organisatie aangemaakt.");
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Aanmaken van organisatie mislukt.");
    }
  }

  async function handleCreateDiscipline(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      await apiRequest("/disciplines", {
        method: "POST",
        body: {
          code: discCode,
          name: discName,
          validity_value: discValidityValue ? Number(discValidityValue) : null,
          validity_unit: discValidityValue ? discValidityUnit : null,
        },
      });
      setDiscCode("");
      setDiscName("");
      setDiscValidityValue("");
      setMessage("Discipline aangemaakt.");
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Aanmaken van discipline mislukt.");
    }
  }

  async function handleCreateDocumentType(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      await apiRequest("/document-types", {
        method: "POST",
        body: {
          code: typeCode,
          name: typeName,
          requires_inspection_data: typeRequiresInspection,
        },
      });
      setTypeCode("");
      setTypeName("");
      setTypeRequiresInspection(false);
      setMessage("Documenttype aangemaakt.");
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Aanmaken van documenttype mislukt.");
    }
  }

  return (
    <div>
      <h2>Beheer</h2>
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      <section>
        <h3>Organisaties</h3>
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Naam</th>
              <th>Actief</th>
            </tr>
          </thead>
          <tbody>
            {organizations.map((org) => (
              <tr key={org.id}>
                <td>{org.code}</td>
                <td>{org.name}</td>
                <td>{org.is_active ? "Ja" : "Nee"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <form onSubmit={handleCreateOrganization}>
          <label>
            Code
            <input value={orgCode} onChange={(e) => setOrgCode(e.target.value)} required />
          </label>
          <label>
            Naam
            <input value={orgName} onChange={(e) => setOrgName(e.target.value)} required />
          </label>
          <button type="submit">Organisatie aanmaken</button>
        </form>
      </section>

      <section>
        <h3>Disciplines</h3>
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Naam</th>
              <th>Vervaltermijn</th>
            </tr>
          </thead>
          <tbody>
            {disciplines.map((d) => (
              <tr key={d.id}>
                <td>{d.code}</td>
                <td>{d.name}</td>
                <td>{d.validity_value ? `${d.validity_value} ${d.validity_unit}` : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <form onSubmit={handleCreateDiscipline}>
          <label>
            Code
            <input value={discCode} onChange={(e) => setDiscCode(e.target.value)} required />
          </label>
          <label>
            Naam
            <input value={discName} onChange={(e) => setDiscName(e.target.value)} required />
          </label>
          <label>
            Vervaltermijn (leeg = geen automatische vervaldatum)
            <input
              type="number"
              min="1"
              value={discValidityValue}
              onChange={(e) => setDiscValidityValue(e.target.value)}
            />
          </label>
          <label>
            Eenheid
            <select value={discValidityUnit} onChange={(e) => setDiscValidityUnit(e.target.value)}>
              <option value="day">dag(en)</option>
              <option value="month">maand(en)</option>
              <option value="year">jaar/jaren</option>
            </select>
          </label>
          <button type="submit">Discipline aanmaken</button>
        </form>
      </section>

      <section>
        <h3>Documenttypes</h3>
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Naam</th>
              <th>Vereist keuringsgegevens</th>
            </tr>
          </thead>
          <tbody>
            {documentTypes.map((t) => (
              <tr key={t.id}>
                <td>{t.code}</td>
                <td>{t.name}</td>
                <td>{t.requires_inspection_data ? "Ja" : "Nee"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <form onSubmit={handleCreateDocumentType}>
          <label>
            Code
            <input value={typeCode} onChange={(e) => setTypeCode(e.target.value)} required />
          </label>
          <label>
            Naam
            <input value={typeName} onChange={(e) => setTypeName(e.target.value)} required />
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={typeRequiresInspection}
              onChange={(e) => setTypeRequiresInspection(e.target.checked)}
            />
            Vereist keuringsgegevens (keuringsdatum, status, vervaldatum)
          </label>
          <button type="submit">Documenttype aanmaken</button>
        </form>
      </section>
    </div>
  );
}
