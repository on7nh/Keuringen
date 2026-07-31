import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { ApiError, apiRequest, getCurrentSessionId } from "../api/client";
import type { Passkey, RecoveryCodesStatus, TotpSetupResponse, UserSession } from "../api/types";
import { createPasskeyCredential, isWebAuthnSupported } from "../api/webauthn";
import { useStepUp, withStepUp } from "../context/StepUpContext";

export function SecurityPage() {
  const { requestStepUp } = useStepUp();

  const [passkeys, setPasskeys] = useState<Passkey[]>([]);
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [recoveryStatus, setRecoveryStatus] = useState<RecoveryCodesStatus | null>(null);
  const [activeMethods, setActiveMethods] = useState<string[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [newDeviceName, setNewDeviceName] = useState("");
  const [totpSetup, setTotpSetup] = useState<TotpSetupResponse | null>(null);
  const [totpCode, setTotpCode] = useState("");
  const [newRecoveryCodes, setNewRecoveryCodes] = useState<string[] | null>(null);
  const [recoveryConfirmed, setRecoveryConfirmed] = useState(false);

  async function loadAll() {
    try {
      const [pk, ss, rc, me] = await Promise.all([
        apiRequest<Passkey[]>("/auth/passkey/list"),
        apiRequest<UserSession[]>("/auth/sessions"),
        apiRequest<RecoveryCodesStatus>("/auth/recovery-codes/status"),
        apiRequest<{ active_strong_auth_methods: string[] }>("/auth/me"),
      ]);
      setPasskeys(pk);
      setSessions(ss);
      setRecoveryStatus(rc);
      setActiveMethods(me.active_strong_auth_methods);
    } catch {
      setError("Kon beveiligingsgegevens niet laden.");
    }
  }

  useEffect(() => {
    void loadAll();
    setCurrentSessionId(getCurrentSessionId());
  }, []);

  async function handleAddPasskey(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const options = await withStepUp(requestStepUp, "PASSKEY_REGISTER", () =>
        apiRequest<{ challenge_id: string; options: unknown }>("/auth/passkey/register/options", {
          method: "POST",
          body: { device_name: newDeviceName },
        }),
      );
      const credential = await createPasskeyCredential(
        options.options as Parameters<typeof createPasskeyCredential>[0],
      );
      await apiRequest("/auth/passkey/register/verify", {
        method: "POST",
        body: { challenge_id: options.challenge_id, device_name: newDeviceName, credential },
      });
      setNewDeviceName("");
      setMessage("Passkey toegevoegd.");
      await loadAll();
    } catch {
      setError("Passkey toevoegen is mislukt of geannuleerd.");
    }
  }

  async function handleRenamePasskey(id: string, currentName: string) {
    const deviceName = window.prompt("Nieuwe naam voor deze passkey:", currentName);
    if (!deviceName) return;
    try {
      await apiRequest(`/auth/passkey/${id}`, { method: "PATCH", body: { device_name: deviceName } });
      await loadAll();
    } catch {
      setError("Naam wijzigen mislukt.");
    }
  }

  async function handleRevokePasskey(id: string, deviceName: string) {
    if (!window.confirm(`Passkey "${deviceName}" verwijderen? Aanmelden met dit apparaat is dan niet meer mogelijk.`))
      return;
    setError(null);
    setMessage(null);
    try {
      await withStepUp(requestStepUp, "PASSKEY_REVOKE", () => apiRequest(`/auth/passkey/${id}`, { method: "DELETE" }));
      setMessage("Passkey ingetrokken.");
      await loadAll();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Intrekken mislukt.");
    }
  }

  async function handleTotpSetup() {
    setError(null);
    setMessage(null);
    try {
      const result = await withStepUp(requestStepUp, "TOTP_SETUP", () =>
        apiRequest<TotpSetupResponse>("/auth/totp/setup", { method: "POST" }),
      );
      setTotpSetup(result);
    } catch {
      setError("TOTP instellen mislukt.");
    }
  }

  async function handleTotpConfirm(e: FormEvent) {
    e.preventDefault();
    if (!totpSetup) return;
    setError(null);
    try {
      await apiRequest("/auth/totp/confirm", {
        method: "POST",
        body: { registration_id: totpSetup.registration_id, code: totpCode },
      });
      setTotpSetup(null);
      setTotpCode("");
      setMessage("TOTP geactiveerd.");
      await loadAll();
    } catch {
      setError("Ongeldige code.");
    }
  }

  async function handleTotpRevoke() {
    if (!window.confirm("Authenticator-app verwijderen?")) return;
    setError(null);
    setMessage(null);
    try {
      await withStepUp(requestStepUp, "TOTP_REVOKE", () => apiRequest("/auth/totp", { method: "DELETE" }));
      setMessage("TOTP verwijderd.");
      await loadAll();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Verwijderen mislukt.");
    }
  }

  async function handleGenerateRecoveryCodes() {
    if (
      recoveryStatus &&
      recoveryStatus.remaining_count > 0 &&
      !window.confirm("Nieuwe herstelcodes maakt alle bestaande codes ongeldig. Doorgaan?")
    )
      return;
    setError(null);
    setMessage(null);
    try {
      const result = await withStepUp(requestStepUp, "RECOVERY_CODES_GENERATE", () =>
        apiRequest<{ codes: string[] }>("/auth/recovery-codes/generate", { method: "POST" }),
      );
      setNewRecoveryCodes(result.codes);
      setRecoveryConfirmed(false);
      await loadAll();
    } catch {
      setError("Genereren van herstelcodes mislukt.");
    }
  }

  async function handleRevokeSession(id: string) {
    setError(null);
    setMessage(null);
    try {
      await withStepUp(requestStepUp, "SESSION_REVOKE", () => apiRequest(`/auth/sessions/${id}`, { method: "DELETE" }));
      setMessage("Sessie beëindigd.");
      await loadAll();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Beëindigen mislukt.");
    }
  }

  async function handleRevokeAllOtherSessions() {
    if (!window.confirm("Alle andere sessies beëindigen?")) return;
    setError(null);
    setMessage(null);
    try {
      await withStepUp(requestStepUp, "SESSIONS_REVOKE_ALL", () => apiRequest("/auth/logout-all", { method: "POST" }));
      setMessage("Alle andere sessies beëindigd.");
      await loadAll();
    } catch {
      setError("Beëindigen mislukt.");
    }
  }

  const canRemoveMethod = activeMethods.length > 1;

  return (
    <div>
      <h2>Beveiliging en aanmelden</h2>
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      <section>
        <h3>Passkeys</h3>
        <table>
          <thead>
            <tr>
              <th>Naam</th>
              <th>Type</th>
              <th>Geregistreerd</th>
              <th>Laatst gebruikt</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {passkeys.map((pk) => (
              <tr key={pk.id}>
                <td>{pk.device_name}</td>
                <td>{pk.authenticator_attachment === "platform" ? "Ingebouwd apparaat" : "Security key"}</td>
                <td>{new Date(pk.registered_at).toLocaleDateString()}</td>
                <td>{pk.last_used_at ? new Date(pk.last_used_at).toLocaleString() : "Nooit"}</td>
                <td>
                  <button type="button" className="link-button" onClick={() => handleRenamePasskey(pk.id, pk.device_name)}>
                    Naam wijzigen
                  </button>{" "}
                  <button
                    type="button"
                    className="link-button"
                    disabled={!canRemoveMethod}
                    title={!canRemoveMethod ? "Voeg eerst een andere methode toe." : undefined}
                    onClick={() => handleRevokePasskey(pk.id, pk.device_name)}
                  >
                    Verwijderen
                  </button>
                </td>
              </tr>
            ))}
            {passkeys.length === 0 && (
              <tr>
                <td colSpan={5}>Geen passkeys geregistreerd.</td>
              </tr>
            )}
          </tbody>
        </table>

        {isWebAuthnSupported() ? (
          <form onSubmit={handleAddPasskey}>
            <label>
              Naam van apparaat of sleutel
              <input
                value={newDeviceName}
                onChange={(e) => setNewDeviceName(e.target.value)}
                placeholder="bv. Laptop kantoor"
                required
              />
            </label>
            <button type="submit">Passkey toevoegen</button>
          </form>
        ) : (
          <p className="hint">Deze browser ondersteunt geen passkeys.</p>
        )}
      </section>

      <section>
        <h3>Authenticator-app (TOTP)</h3>
        {activeMethods.includes("TOTP") ? (
          <>
            <p>Actief.</p>
            <button type="button" disabled={!canRemoveMethod} onClick={handleTotpRevoke}>
              Verwijderen
            </button>
            {!canRemoveMethod && (
              <p className="hint">Voeg eerst een passkey toe voordat u dit kunt verwijderen.</p>
            )}
          </>
        ) : totpSetup ? (
          <form onSubmit={handleTotpConfirm}>
            <img src={totpSetup.qr_code_data_uri} alt="QR-code voor authenticator-app" width={160} height={160} />
            <p>
              Handmatige sleutel: <code>{totpSetup.secret}</code>
            </p>
            <p className="hint">Deel deze QR-code of sleutel met niemand.</p>
            <label>
              Bevestigingscode
              <input
                type="text"
                inputMode="numeric"
                required
                autoFocus
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
              />
            </label>
            <button type="submit">Bevestigen</button>
            <button type="button" className="link-button" onClick={() => setTotpSetup(null)}>
              Annuleren
            </button>
          </form>
        ) : (
          <button type="button" onClick={handleTotpSetup}>
            Authenticator-app instellen
          </button>
        )}
      </section>

      <section>
        <h3>Herstelcodes</h3>
        {newRecoveryCodes ? (
          <div>
            <p className="hint">Deze codes worden slechts eenmaal getoond. Bewaar ze veilig.</p>
            <ul>
              {newRecoveryCodes.map((code) => (
                <li key={code}>
                  <code>{code}</code>
                </li>
              ))}
            </ul>
            <button type="button" onClick={() => navigator.clipboard.writeText(newRecoveryCodes.join("\n"))}>
              Kopiëren
            </button>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={recoveryConfirmed}
                onChange={(e) => setRecoveryConfirmed(e.target.checked)}
              />
              Ik heb mijn herstelcodes veilig bewaard
            </label>
            <button type="button" disabled={!recoveryConfirmed} onClick={() => setNewRecoveryCodes(null)}>
              Sluiten
            </button>
          </div>
        ) : (
          <>
            <p>
              {recoveryStatus?.remaining_count ?? 0} resterende code(s)
              {recoveryStatus?.generated_at && ` - gegenereerd op ${new Date(recoveryStatus.generated_at).toLocaleDateString()}`}
            </p>
            <button type="button" onClick={handleGenerateRecoveryCodes}>
              Nieuwe herstelcodes genereren
            </button>
          </>
        )}
      </section>

      <section>
        <h3>Actieve sessies</h3>
        <table>
          <thead>
            <tr>
              <th>Apparaat</th>
              <th>IP-adres</th>
              <th>Methode</th>
              <th>Laatste activiteit</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.id}>
                <td>{s.device_label ?? "Onbekend apparaat"}</td>
                <td>{s.ip_address ?? "-"}</td>
                <td>{s.authentication_method}</td>
                <td>{new Date(s.last_seen_at).toLocaleString()}</td>
                <td>
                  {s.id === currentSessionId ? (
                    <span className="hint">Huidige sessie</span>
                  ) : (
                    <button type="button" className="link-button" onClick={() => handleRevokeSession(s.id)}>
                      Beëindigen
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button type="button" onClick={handleRevokeAllOtherSessions}>
          Alle andere sessies beëindigen
        </button>
      </section>
    </div>
  );
}
