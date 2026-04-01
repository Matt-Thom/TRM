/** Standard API response envelope */
export interface APIResponse<T> {
  data: T | null;
  meta: {
    request_id?: string;
  };
  errors: Array<{
    code: string;
    message: string;
    field?: string;
  }>;
}

/** Risk entity */
export interface Risk {
  id: string;
  title: string;
  description: string;
  threat_source: string;
  vulnerability: string;
  asset_at_risk: string;
  category: string;
  status: "Open" | "Under Review" | "Mitigated" | "Accepted" | "Closed";
  likelihood: number;
  impact: number;
  inherent_risk_score: number;
  riskOwnerId: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface RiskListResponse {
  items: Risk[];
  next_cursor: string | null;
  has_more: boolean;
}
