import { createContext, useCallback, useContext, useState } from "react";
import type { ReactNode } from "react";

import { getErrorCode } from "../api/client";
import { StepUpModal } from "../components/StepUpModal";

interface PendingStepUp {
  intendedAction: string;
  resolve: () => void;
  reject: (reason: Error) => void;
}

interface StepUpContextValue {
  requestStepUp: (intendedAction: string) => Promise<void>;
}

const StepUpContext = createContext<StepUpContextValue | undefined>(undefined);

export function StepUpProvider({ children }: { children: ReactNode }) {
  const [pending, setPending] = useState<PendingStepUp | null>(null);

  const requestStepUp = useCallback((intendedAction: string) => {
    return new Promise<void>((resolve, reject) => {
      setPending({ intendedAction, resolve, reject });
    });
  }, []);

  function handleSuccess() {
    pending?.resolve();
    setPending(null);
  }

  function handleCancel() {
    pending?.reject(new Error("STEP_UP_CANCELLED"));
    setPending(null);
  }

  return (
    <StepUpContext.Provider value={{ requestStepUp }}>
      {children}
      {pending && (
        <StepUpModal intendedAction={pending.intendedAction} onSuccess={handleSuccess} onCancel={handleCancel} />
      )}
    </StepUpContext.Provider>
  );
}

export function useStepUp(): StepUpContextValue {
  const ctx = useContext(StepUpContext);
  if (!ctx) throw new Error("useStepUp must be used within StepUpProvider");
  return ctx;
}

/** Runs `action`; if it fails with STEP_UP_REQUIRED, prompts for step-up and
 * retries once. Mirrors docs/07 §19: "na succes automatische voortzetting
 * van de oorspronkelijke actie." */
export async function withStepUp<T>(
  requestStepUp: (intendedAction: string) => Promise<void>,
  intendedAction: string,
  action: () => Promise<T>,
): Promise<T> {
  try {
    return await action();
  } catch (err) {
    if (getErrorCode(err) === "STEP_UP_REQUIRED") {
      await requestStepUp(intendedAction);
      return action();
    }
    throw err;
  }
}
