"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import { Risk } from "@/types";

export default function RiskDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const isNew = id === "new";

  const [risk, setRisk] = useState<Partial<Risk>>({
    title: "",
    description: "",
    threat_source: "",
    vulnerability: "",
    asset_at_risk: "",
    category: "Organisational",
    status: "Open",
    likelihood: 3,
    impact: 3,
  });

  useEffect(() => {
    if (!isNew) {
      api.get<{ data: Risk }>(`/api/v1/risks/${id}`).then(res => setRisk(res.data.data));
    }
  }, [id, isNew]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isNew) {
        await api.post("/api/v1/risks", risk);
      } else {
        await api.put(`/api/v1/risks/${id}`, risk);
      }
      router.push("/dashboard");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-8 bg-[#f7f9fd] min-h-screen">
      <button onClick={() => router.back()} className="text-sm text-gray-500 hover:text-gray-700 mb-6">← Back to Dashboard</button>

      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 max-w-2xl">
        <h1 className="text-2xl font-semibold mb-6">{isNew ? "Create New Risk" : "Edit Risk"}</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input type="text" value={risk.title || ""} onChange={e => setRisk({...risk, title: e.target.value})} className="w-full border rounded p-2" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea value={risk.description || ""} onChange={e => setRisk({...risk, description: e.target.value})} className="w-full border rounded p-2" rows={3} required />
          </div>
          <div className="grid grid-cols-2 gap-4">
             <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Threat Source</label>
                <input type="text" value={risk.threat_source || ""} onChange={e => setRisk({...risk, threat_source: e.target.value})} className="w-full border rounded p-2" required />
            </div>
             <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Vulnerability</label>
                <input type="text" value={risk.vulnerability || ""} onChange={e => setRisk({...risk, vulnerability: e.target.value})} className="w-full border rounded p-2" required />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Asset at Risk</label>
            <input type="text" value={risk.asset_at_risk || ""} onChange={e => setRisk({...risk, asset_at_risk: e.target.value})} className="w-full border rounded p-2" required />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select value={risk.category || "Organisational"} onChange={e => setRisk({...risk, category: e.target.value as any})} className="w-full border rounded p-2">
                <option value="Organisational">Organisational</option>
                <option value="People">People</option>
                <option value="Physical">Physical</option>
                <option value="Technological">Technological</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select value={risk.status || "Open"} onChange={e => setRisk({...risk, status: e.target.value as any})} className="w-full border rounded p-2">
                <option value="Open">Open</option>
                <option value="Under Review">Under Review</option>
                <option value="Mitigated">Mitigated</option>
                <option value="Accepted">Accepted</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Likelihood (1-5)</label>
              <input type="number" min="1" max="5" value={risk.likelihood || 1} onChange={e => setRisk({...risk, likelihood: parseInt(e.target.value)})} className="w-full border rounded p-2" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Impact (1-5)</label>
              <input type="number" min="1" max="5" value={risk.impact || 1} onChange={e => setRisk({...risk, impact: parseInt(e.target.value)})} className="w-full border rounded p-2" required />
            </div>
          </div>

          <button type="submit" className="w-full bg-blue-600 text-white font-medium py-2 px-4 rounded hover:bg-blue-700 transition mt-4">
            {isNew ? "Create Risk" : "Update Risk"}
          </button>
        </form>
      </div>
    </div>
  );
}
