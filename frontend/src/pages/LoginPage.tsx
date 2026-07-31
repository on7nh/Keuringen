import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { LoginResponse } from "../api/types";
import { isWebAuthnSupported, requestPasskeyAssertion } from "../api/webauthn";
import { useAuth } from "../context/AuthContext";

type Step = "credentials" | "totp";

export function LoginPage() {
  const { onLoginSuccess } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>("credentials");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [challengeId, setChallengeId] = useState<string | null>(null);
  const [allowedMethods, setAllowedMethods] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleCredentialsSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const response = await apiRequest<LoginResponse>("/auth/login", {
        method: "POST",
        body: { email, password },
        skipAuth: true,
      });

      if (response.status === "OK" && response.access_token && response.refresh_token) {
        await onLoginSuccess(response.access_token, response.refresh_token);
        navigate("/");
        return;
      }

      if (response.status === "STRONG_AUTH_REQUIRED") {
        setChallengeId(response.challenge_id ?? null);
        setAllowedMethods(response.allowed_methods);
        if (response.allowed_methods.includes("TOTP")) {
          setStep("totp");
        } else {
          setError(
            "Sterke authenticatie is vereist maar er is geen geregistreerde methode beschikbaar. Neem contact op met een beheerder.",
          );
        }
      }
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Aanmelden mislukt.");
    } finally {
      setBusy(false);
    }
  }

  async function handlePasskeyLogin() {
    setError(null);
    setBusy(true);
    try {
      const optionsResponse = await apiRequest<{ challenge_id: string; options: unknown }>(
        "/auth/passkey/login/options",
        { method: "POST", body: email ? { email } : {}, skipAuth: true },
      );
      const credential = await requestPasskeyAssertion(
        optionsResponse.options as Parameters<typeof requestPasskeyAssertion>[0],
      );
      const response = await apiRequest<LoginResponse>("/auth/passkey/login/verify", {
        method: "POST",
        body: { challenge_id: optionsResponse.challenge_id, credential },
        skipAuth: true,
      });
      if (response.access_token && response.refresh_token) {
        await onLoginSuccess(response.access_token, response.refresh_token);
        navigate("/");
      }
    } catch (err) {
      setError(err instanceof ApiError ? "Passkey-aanmelding mislukt." : "Passkey niet beschikbaar of geannuleerd.");
    } finally {
      setBusy(false);
    }
  }

  async function handleTotpSubmit(e: FormEvent) {
    e.preventDefault();
    if (!challengeId) return;
    setError(null);
    setBusy(true);
    try {
      const response = await apiRequest<LoginResponse>("/auth/totp/verify", {
        method: "POST",
        body: { challenge_id: challengeId, code },
        skipAuth: true,
      });
      if (response.access_token && response.refresh_token) {
        await onLoginSuccess(response.access_token, response.refresh_token);
        navigate("/");
      }
    } catch (err) {
      setError(err instanceof ApiError ? "Ongeldige code." : "Verificatie mislukt.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Digitaal Keurings- en Documentbeheer</h1>

        {step === "credentials" && (
          <form onSubmit={handleCredentialsSubmit}>
            <label>
              E-mailadres
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="username"
              />
            </label>
            <label>
              Wachtwoord
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </label>
            {error && <p className="error">{error}</p>}
            <button type="submit" disabled={busy}>
              Aanmelden
            </button>
            {isWebAuthnSupported() && (
              <button type="button" className="link-button" disabled={busy} onClick={handlePasskeyLogin}>
                Aanmelden met Passkey
              </button>
            )}
          </form>
        )}

        {step === "totp" && (
          <form onSubmit={handleTotpSubmit}>
            <p>Voer de code uit uw authenticator-app in.</p>
            <label>
              TOTP-code
              <input
                type="text"
                inputMode="numeric"
                required
                value={code}
                onChange={(e) => setCode(e.target.value)}
                autoFocus
              />
            </label>
            {error && <p className="error">{error}</p>}
            <button type="submit" disabled={busy}>
              Bevestigen
            </button>
            <button
              type="button"
              className="link-button"
              onClick={() => {
                setStep("credentials");
                setError(null);
              }}
            >
              Terug
            </button>
          </form>
        )}

        {allowedMethods.length > 0 && step === "totp" && !allowedMethods.includes("TOTP") && (
          <p className="hint">Beschikbare methoden: {allowedMethods.join(", ")}</p>
        )}
      </div>
    </div>
  );
}
