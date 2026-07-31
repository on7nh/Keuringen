export type Language = "nl" | "en";

export const SUPPORTED_LANGUAGES: { code: Language; label: string }[] = [
  { code: "nl", label: "Nederlands" },
  { code: "en", label: "English" },
];

/**
 * Groundwork for the "meertaligheid vanaf de basisarchitectuur" principle
 * (docs/07 §8). This is not yet a full translation of every screen - it
 * covers navigation, the login flow and common actions, which is enough to
 * prove the architecture and extend page by page. See PROGRESS.md.
 */
export const translations: Record<Language, Record<string, string>> = {
  nl: {
    "app.title": "Digitaal Keurings- en Documentbeheer",
    "nav.dashboard": "Dashboard",
    "nav.sites": "Sites",
    "nav.documents": "Documenten",
    "nav.inspections": "Keuringen",
    "nav.admin": "Beheer",
    "nav.status": "Systeemstatus",
    "nav.logout": "Afmelden",

    "common.cancel": "Annuleren",
    "common.confirm": "Bevestigen",
    "common.save": "Opslaan",
    "common.close": "Sluiten",
    "common.loading": "Laden...",

    "login.email": "E-mailadres",
    "login.password": "Wachtwoord",
    "login.submit": "Aanmelden",
    "login.withPasskey": "Aanmelden met Passkey",
    "login.totpPrompt": "Voer de code uit uw authenticator-app in.",
    "login.totpCode": "TOTP-code",
    "login.back": "Terug",
    "login.troubleSigningIn": "Problemen met aanmelden?",
    "login.troubleSigningInHelp":
      "Neem contact op met uw beheerder om een andere aanmeldmethode te laten registreren of een gecontroleerde herstelprocedure te starten.",
    "login.genericError": "Aanmelden is niet gelukt. Controleer uw gegevens of gebruik een andere methode.",

    "setupBanner.message":
      "Sterke authenticatie is verplicht voor uw account, maar u hebt nog geen passkey of authenticator-app geregistreerd.",
    "setupBanner.action": "Nu instellen",

    "security.title": "Beveiliging en aanmelden",
    "security.passkeys": "Passkeys",
    "security.totp": "Authenticator-app (TOTP)",
    "security.recoveryCodes": "Herstelcodes",
    "security.sessions": "Actieve sessies",
  },
  en: {
    "app.title": "Digital Inspection & Document Management",
    "nav.dashboard": "Dashboard",
    "nav.sites": "Sites",
    "nav.documents": "Documents",
    "nav.inspections": "Inspections",
    "nav.admin": "Admin",
    "nav.status": "System status",
    "nav.logout": "Sign out",

    "common.cancel": "Cancel",
    "common.confirm": "Confirm",
    "common.save": "Save",
    "common.close": "Close",
    "common.loading": "Loading...",

    "login.email": "Email address",
    "login.password": "Password",
    "login.submit": "Sign in",
    "login.withPasskey": "Sign in with Passkey",
    "login.totpPrompt": "Enter the code from your authenticator app.",
    "login.totpCode": "TOTP code",
    "login.back": "Back",
    "login.troubleSigningIn": "Trouble signing in?",
    "login.troubleSigningInHelp":
      "Contact your administrator to register another sign-in method or start a supervised recovery procedure.",
    "login.genericError": "Sign-in was unsuccessful. Check your details or use another method.",

    "setupBanner.message":
      "Strong authentication is required for your account, but you haven't registered a passkey or authenticator app yet.",
    "setupBanner.action": "Set up now",

    "security.title": "Security and sign-in",
    "security.passkeys": "Passkeys",
    "security.totp": "Authenticator app (TOTP)",
    "security.recoveryCodes": "Recovery codes",
    "security.sessions": "Active sessions",
  },
};
