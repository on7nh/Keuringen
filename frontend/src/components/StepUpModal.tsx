import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { apiRequest } from "../api/client";
import { isWebAuthnSupported, requestPasskeyAssertion } from "../api/webauthn";

interface StepUpOptions {
  step_up_id: string;
  allowed_methods: string[];
  webauthn_options: Parameters<typeof requestPasskeyAssertion>[0] | null;
}

interface Props {
  intendedAction: string;
  onSuccess: () => void;
  onCancel: () => void;
}

/** Compact modal for step-up authentication, per docs/07 §19: explains why
 * confirmation is needed, offers Passkey first then TOTP, and resumes the
 * original action on success without losing the user's place. */
export function StepUpModal({ intendedAction, onSuccess, onCancel }: Props) {
  const [options, setOptions] = useState<StepUpOptions | null>(null);
  const [method, setMethod] = useState<"passkey" | "totp" | null>(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    apiRequest<StepUpOptions>("/auth/step-up/options", {
      method: "POST",
      body: { intended_action: intendedAction },
    })
      .then((result) => {
        setOptions(result);
        if (result.allowed_methods.includes("PASSKEY") && result.webauthn_options && isWebAuthnSupported()) {
          setMethod("passkey");
        } else if (result.allowed_methods.includes("TOTP")) {
          setMethod("totp");
        }
      })
      .catch(() => setError("Kon de bevestiging niet starten."));
  }, [intendedAction]);

  async function handlePasskeyConfirm() {
    if (!options?.webauthn_options) return;
    setError(null);
    setBusy(true);
    try {
      const credential = await requestPasskeyAssertion(options.webauthn_options);
      await apiRequest("/auth/step-up/passkey/verify", {
        method: "POST",
        body: { step_up_id: options.step_up_id, credential },
      });
      onSuccess();
    } catch {
      setError("Bevestiging met passkey is mislukt of geannuleerd.");
    } finally {
      setBusy(false);
    }
  }

  async function handleTotpConfirm(e: FormEvent) {
    e.preventDefault();
    if (!options) return;
    setError(null);
    setBusy(true);
    try {
      await apiRequest("/auth/step-up/totp/verify", {
        method: "POST",
        body: { step_up_id: options.step_up_id, code },
      });
      onSuccess();
    } catch {
      setError("Ongeldige code.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Aanvullende verificatie">
      <div className="modal-card">
        <h3>Aanvullende verificatie vereist</h3>
        <p>Voor deze actie is een recente bevestiging van uw identiteit nodig.</p>

        {error && <p className="error">{error}</p>}

        {!options && !error && <p>Laden...</p>}

        {options && method === "passkey" && (
          <>
            <button type="button" onClick={handlePasskeyConfirm} disabled={busy}>
              Bevestigen met passkey
            </button>
            {options.allowed_methods.includes("TOTP") && (
              <button type="button" className="link-button" onClick={() => setMethod("totp")}>
                Authenticator-code gebruiken
              </button>
            )}
          </>
        )}

        {options && method === "totp" && (
          <form onSubmit={handleTotpConfirm}>
            <label>
              Authenticator-code
              <input
                type="text"
                inputMode="numeric"
                autoFocus
                required
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
            </label>
            <button type="submit" disabled={busy}>
              Bevestigen
            </button>
            {options.allowed_methods.includes("PASSKEY") && options.webauthn_options && (
              <button type="button" className="link-button" onClick={() => setMethod("passkey")}>
                Passkey gebruiken
              </button>
            )}
          </form>
        )}

        {options && !options.allowed_methods.length && (
          <p className="error">Geen sterke authenticatiemethode beschikbaar. Neem contact op met een beheerder.</p>
        )}

        <button type="button" className="link-button" onClick={onCancel}>
          Annuleren
        </button>
      </div>
    </div>
  );
}
