export interface LoginResponse {
  status: "STRONG_AUTH_REQUIRED" | "OK";
  challenge_id?: string;
  allowed_methods: string[];
  expires_at?: string;
  access_token?: string;
  refresh_token?: string;
}

export interface Me {
  id: string;
  email: string;
  display_name: string;
  is_system_admin: boolean;
  organization_roles: { organization_id: string; role_id: string }[];
  site_roles: { site_id: string; role_id: string }[];
}

export interface Organization {
  id: string;
  code: string;
  name: string;
  is_active: boolean;
  sharepoint_marking_enabled: boolean;
  default_timezone: string;
}

export interface Site {
  id: string;
  organization_id: string;
  site_number: string;
  code: string;
  name: string;
  storage_code: string;
  is_temporary_site_number: boolean;
  is_active: boolean;
}

export interface Discipline {
  id: string;
  code: string;
  name: string;
  validity_value: number | null;
  validity_unit: string | null;
  is_general: boolean;
  is_active: boolean;
}

export interface DocumentType {
  id: string;
  code: string;
  name: string;
  requires_inspection_data: boolean;
  supports_ai_analysis: boolean;
}

export interface KeuringDocument {
  id: string;
  organization_id: string;
  site_id: string;
  installation_id: string | null;
  discipline_id: string;
  document_type_id: string;
  title: string | null;
  document_date: string | null;
  document_date_source: string | null;
  ai_status: string;
  validation_status: string;
  sharepoint_marked: boolean;
  row_version: number;
}

export interface InspectionStatus {
  id: string;
  code: string;
  label: string;
  display_order: number;
}

export interface SystemStatusCheck {
  name: string;
  label: string;
  status: "ok" | "error" | "not_configured" | "unknown" | "update_available";
  detail: string | null;
  latency_ms: number | null;
}

export interface SystemStatus {
  status: "ok" | "degraded";
  checks: SystemStatusCheck[];
}

export interface InspectionReport {
  id: string;
  document_id: string;
  inspection_date: string | null;
  inspection_date_source: string | null;
  report_date: string | null;
  expiry_date: string | null;
  inspection_status_id: string;
  certificate_number: string | null;
  remarks: string | null;
  validated_at: string | null;
}
