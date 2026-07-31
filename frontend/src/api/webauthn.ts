function base64UrlToBuffer(value: string): ArrayBuffer {
  const padded = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(value.length + ((4 - (value.length % 4)) % 4), "=");
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes.buffer;
}

function bufferToBase64Url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function isWebAuthnSupported(): boolean {
  return typeof window !== "undefined" && !!window.PublicKeyCredential;
}

export async function requestPasskeyAssertion(
  optionsJson: PublicKeyCredentialRequestOptionsJSON,
): Promise<Record<string, unknown>> {
  const publicKey = {
    ...optionsJson,
    challenge: base64UrlToBuffer(optionsJson.challenge),
    allowCredentials: optionsJson.allowCredentials?.map((cred) => ({
      id: base64UrlToBuffer(cred.id as unknown as string),
      type: "public-key" as const,
      transports: cred.transports,
    })),
  } as unknown as PublicKeyCredentialRequestOptions;

  const credential = (await navigator.credentials.get({ publicKey })) as PublicKeyCredential;
  const response = credential.response as AuthenticatorAssertionResponse;

  return {
    id: credential.id,
    rawId: bufferToBase64Url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufferToBase64Url(response.clientDataJSON),
      authenticatorData: bufferToBase64Url(response.authenticatorData),
      signature: bufferToBase64Url(response.signature),
      userHandle: response.userHandle ? bufferToBase64Url(response.userHandle) : null,
    },
  };
}

export async function createPasskeyCredential(
  optionsJson: PublicKeyCredentialCreationOptionsJSON,
): Promise<Record<string, unknown>> {
  const publicKey = {
    ...optionsJson,
    challenge: base64UrlToBuffer(optionsJson.challenge),
    user: { ...optionsJson.user, id: base64UrlToBuffer(optionsJson.user.id as unknown as string) },
    excludeCredentials: optionsJson.excludeCredentials?.map((cred) => ({
      id: base64UrlToBuffer(cred.id as unknown as string),
      type: "public-key" as const,
      transports: cred.transports,
    })),
  } as unknown as PublicKeyCredentialCreationOptions;

  const credential = (await navigator.credentials.create({ publicKey })) as PublicKeyCredential;
  const response = credential.response as AuthenticatorAttestationResponse;

  return {
    id: credential.id,
    rawId: bufferToBase64Url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufferToBase64Url(response.clientDataJSON),
      attestationObject: bufferToBase64Url(response.attestationObject),
      transports: response.getTransports ? response.getTransports() : [],
    },
  };
}

// Minimal shapes matching what the backend's `options_to_json` returns.
interface PublicKeyCredentialRequestOptionsJSON {
  challenge: string;
  rpId?: string;
  timeout?: number;
  userVerification?: string;
  allowCredentials?: { id: string; type: string; transports?: string[] }[];
}

interface PublicKeyCredentialCreationOptionsJSON {
  challenge: string;
  rp: { id?: string; name: string };
  user: { id: string; name: string; displayName: string };
  pubKeyCredParams: { type: string; alg: number }[];
  timeout?: number;
  excludeCredentials?: { id: string; type: string; transports?: string[] }[];
  authenticatorSelection?: Record<string, unknown>;
  attestation?: string;
}
