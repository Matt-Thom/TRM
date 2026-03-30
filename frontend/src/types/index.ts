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
  threatSource: string;
  vulnerability: string;
  assetAtRisk: string;
  category: string;
  status: "Open" | "Under Review" | "Mitigated" | "Accepted" | "Closed";
  likelihood: number;
  impact: number;
  inherentRiskScore: number;
  riskOwnerId: string | null;
  createdAt: string;
  updatedAt: string;
}
