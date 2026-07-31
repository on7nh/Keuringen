import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { LoginResponse } from "../api/types";
import { isWebAuthnSupported, requestPasskeyAssertion } from "../api/webauthn";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";

type Step = "credentials" | "totp";

export function LoginPage() {
  const { onLoginSuccess } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>("credentials");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [challengeId, setChallengeId] = useState<string | null>(null);
  const [allowedMethods, setAllowedMethods] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

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
      setError(err instanceof ApiError ? String(err.detail) : t("login.genericError"));
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
      // Per docs/07 §5.4: a cancelled/failed passkey ceremony is not shown
      // as an alarming failure state, just a neutral message to retry.
      setError(err instanceof ApiError ? t("login.genericError") : "Aanmelding geannuleerd. Probeer opnieuw.");
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
      setError(err instanceof ApiError ? "Ongeldige code." : t("login.genericError"));
      setCode("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-card-header">
          <img
            src="/logo.png"
            alt=""
            className="login-logo"
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
          <LanguageSwitcher />
        </div>
        <h1>{t("app.title")}</h1>

        {step === "credentials" && (
          <form onSubmit={handleCredentialsSubmit}>
            <label>
              {t("login.email")}
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="username"
              />
            </label>
            <label>
              {t("login.password")}
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
              {t("login.submit")}
            </button>
            {isWebAuthnSupported() && (
              <button type="button" className="link-button" disabled={busy} onClick={handlePasskeyLogin}>
                {t("login.withPasskey")}
              </button>
            )}
          </form>
        )}

        {step === "totp" && (
          <form onSubmit={handleTotpSubmit}>
            <p>{t("login.totpPrompt")}</p>
            <label>
              {t("login.totpCode")}
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
              {t("common.confirm")}
            </button>
            <button
              type="button"
              className="link-button"
              onClick={() => {
                setStep("credentials");
                setError(null);
              }}
            >
              {t("login.back")}
            </button>
          </form>
        )}

        {allowedMethods.length > 0 && step === "totp" && !allowedMethods.includes("TOTP") && (
          <p className="hint">Beschikbare methoden: {allowedMethods.join(", ")}</p>
        )}

        <button type="button" className="link-button trouble-link" onClick={() => setShowHelp((v) => !v)}>
          {t("login.troubleSigningIn")}
        </button>
        {showHelp && <p className="hint">{t("login.troubleSigningInHelp")}</p>}
      </div>
    </div>
  );
}
