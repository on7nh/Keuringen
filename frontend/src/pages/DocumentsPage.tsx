import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { ApiError, apiRequest } from "../api/client";
import type { AIProposal, Discipline, DocumentType, KeuringDocument, Site } from "../api/types";

const FIELD_LABELS: Record<string, string> = {
  EXAMINATION_DATE: "Datum van onderzoek",
  REPORT_DATE: "Datum van verslag",
  INSPECTION_STATUS: "Keuringsstatus",
};

const STATUS_VALUE_LABELS: Record<string, string> = {
  APPROVED: "Goedgekeurd",
  APPROVED_WITH_REMARKS: "Goedgekeurd met opmerkingen",
  REJECTED: "Afgekeurd",
};

function formatProposedValue(proposal: AIProposal): string {
  if (proposal.field_code === "INSPECTION_STATUS") {
    return STATUS_VALUE_LABELS[proposal.proposed_value.value] ?? proposal.proposed_value.value;
  }
  return proposal.proposed_value.value;
}

export function DocumentsPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [disciplines, setDisciplines] = useState<Discipline[]>([]);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [documents, setDocuments] = useState<KeuringDocument[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [siteId, setSiteId] = useState("");
  const [disciplineId, setDisciplineId] = useState("");
  const [documentTypeId, setDocumentTypeId] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const [reviewDocumentId, setReviewDocumentId] = useState<string | null>(null);
  const [proposals, setProposals] = useState<AIProposal[]>([]);
  const [correctingId, setCorrectingId] = useState<string | null>(null);
  const [correctionValue, setCorrectionValue] = useState("");

  async function loadData() {
    try {
      const [siteList, disciplineList, docTypeList, documentList] = await Promise.all([
        apiRequest<Site[]>("/sites"),
        apiRequest<Discipline[]>("/disciplines"),
        apiRequest<DocumentType[]>("/document-types"),
        apiRequest<KeuringDocument[]>("/documents"),
      ]);
      setSites(siteList);
      setDisciplines(disciplineList);
      setDocumentTypes(docTypeList);
      setDocuments(documentList);
      if (siteList.length > 0) setSiteId((c) => c || siteList[0].id);
      if (disciplineList.length > 0) setDisciplineId((c) => c || disciplineList[0].id);
      if (docTypeList.length > 0) setDocumentTypeId((c) => c || docTypeList[0].id);
    } catch {
      setError("Kon documentgegevens niet laden.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleUpload(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    setError(null);
    setMessage(null);
    try {
      const formData = new FormData();
      formData.append("site_id", siteId);
      formData.append("discipline_id", disciplineId);
      formData.append("document_type_id", documentTypeId);
      formData.append("file", file);

      await apiRequest("/documents/upload", { method: "POST", body: formData, isForm: true });
      setMessage("Document geüpload.");
      setFile(null);
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Upload mislukt.");
    }
  }

  async function openReview(documentId: string) {
    setError(null);
    setReviewDocumentId(documentId);
    setCorrectingId(null);
    try {
      const result = await apiRequest<AIProposal[]>(`/documents/${documentId}/ai-proposals`);
      setProposals(result);
    } catch {
      setError("Kon AI-voorstellen niet laden.");
    }
  }

  async function handleConfirm(proposalId: string) {
    if (!reviewDocumentId) return;
    setError(null);
    try {
      await apiRequest(`/documents/${reviewDocumentId}/ai-proposals/${proposalId}/confirm`, { method: "POST" });
      await openReview(reviewDocumentId);
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Bevestigen mislukt.");
    }
  }

  async function handleCorrect(proposalId: string) {
    if (!reviewDocumentId) return;
    setError(null);
    try {
      await apiRequest(`/documents/${reviewDocumentId}/ai-proposals/${proposalId}/correct`, {
        method: "POST",
        body: { value: correctionValue },
      });
      setCorrectingId(null);
      setCorrectionValue("");
      await openReview(reviewDocumentId);
      await loadData();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Corrigeren mislukt.");
    }
  }

  return (
    <div>
      <h2>Documenten</h2>
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      <table>
        <thead>
          <tr>
            <th>Discipline</th>
            <th>Type</th>
            <th>AI-status</th>
            <th>Validatiestatus</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td>{disciplines.find((d) => d.id === doc.discipline_id)?.name ?? doc.discipline_id}</td>
              <td>{documentTypes.find((t) => t.id === doc.document_type_id)?.name ?? doc.document_type_id}</td>
              <td>{doc.ai_status}</td>
              <td>{doc.validation_status}</td>
              <td>
                {(doc.ai_status === "COMPLETED" || doc.ai_status === "NO_PROPOSALS") && (
                  <button type="button" className="link-button" onClick={() => openReview(doc.id)}>
                    AI-voorstellen
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {reviewDocumentId && (
        <section>
          <h3>AI-voorstellen</h3>
          {proposals.length === 0 && <p>Geen AI-voorstellen voor dit document.</p>}
          <table>
            <thead>
              <tr>
                <th>Veld</th>
                <th>Voorstel</th>
                <th>Zekerheid</th>
                <th>Bron</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {proposals.map((p) => (
                <tr key={p.id}>
                  <td>{FIELD_LABELS[p.field_code] ?? p.field_code}</td>
                  <td>{formatProposedValue(p)}</td>
                  <td>{p.confidence !== null ? `${Math.round(p.confidence * 100)}%` : "-"}</td>
                  <td className="hint">{p.source_snippet ?? "-"}</td>
                  <td>{p.is_reviewed ? "Gecontroleerd" : "Te controleren"}</td>
                  <td>
                    {!p.is_reviewed && correctingId !== p.id && (
                      <>
                        <button type="button" className="link-button" onClick={() => handleConfirm(p.id)}>
                          Bevestigen
                        </button>{" "}
                        <button
                          type="button"
                          className="link-button"
                          onClick={() => {
                            setCorrectingId(p.id);
                            setCorrectionValue(p.proposed_value.value);
                          }}
                        >
                          Corrigeren
                        </button>
                      </>
                    )}
                    {correctingId === p.id && (
                      <span>
                        {p.field_code === "INSPECTION_STATUS" ? (
                          <select value={correctionValue} onChange={(e) => setCorrectionValue(e.target.value)}>
                            {Object.entries(STATUS_VALUE_LABELS).map(([code, label]) => (
                              <option key={code} value={code}>
                                {label}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type="date"
                            value={correctionValue}
                            onChange={(e) => setCorrectionValue(e.target.value)}
                          />
                        )}
                        <button type="button" onClick={() => handleCorrect(p.id)}>
                          Opslaan
                        </button>
                        <button type="button" className="link-button" onClick={() => setCorrectingId(null)}>
                          Annuleren
                        </button>
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button type="button" className="link-button" onClick={() => setReviewDocumentId(null)}>
            Sluiten
          </button>
        </section>
      )}

      <h3>Document uploaden</h3>
      <form onSubmit={handleUpload}>
        <label>
          Site
          <select value={siteId} onChange={(e) => setSiteId(e.target.value)} required>
            {sites.map((site) => (
              <option key={site.id} value={site.id}>
                {site.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Discipline
          <select value={disciplineId} onChange={(e) => setDisciplineId(e.target.value)} required>
            {disciplines.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Documenttype
          <select value={documentTypeId} onChange={(e) => setDocumentTypeId(e.target.value)} required>
            {documentTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Bestand (PDF, JPG, DWG, XLSX - max 100 MB)
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.dwg,.xlsx"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            required
          />
        </label>
        <button type="submit">Uploaden</button>
      </form>
    </div>
  );
}
