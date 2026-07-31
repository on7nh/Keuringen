import type { Language } from "../i18n/translations";
import { SUPPORTED_LANGUAGES } from "../i18n/translations";
import { useLanguage } from "../context/LanguageContext";

export function LanguageSwitcher({ className }: { className?: string }) {
  const { language, setLanguage } = useLanguage();

  return (
    <select
      className={className}
      value={language}
      onChange={(e) => setLanguage(e.target.value as Language)}
      aria-label="Taal / Language"
    >
      {SUPPORTED_LANGUAGES.map((option) => (
        <option key={option.code} value={option.code}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
