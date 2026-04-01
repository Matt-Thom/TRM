"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { Risk, RiskListResponse } from "@/types";

export default function DashboardPage() {
  const [risks, setRisks] = useState<Risk[]>([]);
  const router = useRouter();

  useEffect(() => {
    async function fetchRisks() {
      try {
        const res = await api.get<{ data: RiskListResponse }>("/api/v1/risks");
        setRisks(res.data.data.items);
      } catch (err) {
        console.error("Failed to load risks", err);
      }
    }
    fetchRisks();
  }, []);

  const totalRisks = risks.length;
  const highRisks = risks.filter(r => r.inherent_risk_score >= 10).length;
  const overdueRisks = risks.filter(r => r.status === "Open").length; // Simplified
  const avgScore = totalRisks ? (risks.reduce((acc, r) => acc + r.inherent_risk_score, 0) / totalRisks).toFixed(1) : "0";

  return (
    <div className="p-8 bg-[#f7f9fd] min-h-screen font-inter">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-semibold tracking-tighter text-[#191c1f]">Risk Dashboard</h1>
          <p className="text-[#45474c] mt-1 text-sm">Overview of the organization's risk posture.</p>
        </div>
        <button onClick={() => router.push("/dashboard/risks/new")} className="bg-gradient-to-r from-[#091426] to-[#1e293b] text-white px-4 py-2 rounded-md font-medium text-sm shadow-sm hover:opacity-90 transition">
          + Add Risk
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col justify-between">
          <div className="text-[#45474c] text-sm font-medium tracking-wide uppercase mb-2">Total Risks</div>
          <div className="text-4xl font-bold tracking-tighter text-[#191c1f]">{totalRisks}</div>
        </div>
        <div className="bg-[#5a0008] rounded-xl p-6 shadow-sm flex flex-col justify-between">
          <div className="text-[#ff5250] text-sm font-medium tracking-wide uppercase mb-2">High & Critical</div>
          <div className="text-4xl font-bold tracking-tighter text-white">{highRisks}</div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col justify-between">
          <div className="text-[#45474c] text-sm font-medium tracking-wide uppercase mb-2">Open Risks</div>
          <div className="text-4xl font-bold tracking-tighter text-[#191c1f]">{overdueRisks}</div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col justify-between">
          <div className="text-[#45474c] text-sm font-medium tracking-wide uppercase mb-2">Avg Inherent Score</div>
          <div className="text-4xl font-bold tracking-tighter text-[#191c1f]">{avgScore}</div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-[#f2f4f8]">
          <h2 className="text-lg font-semibold text-[#191c1f]">Risk Register</h2>
          <button className="text-[#45474c] text-sm font-medium bg-white px-3 py-1.5 rounded border border-gray-200 hover:bg-gray-50">Filter</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white border-b border-gray-100">
                <th className="px-6 py-3 text-[#45474c] text-xs uppercase tracking-widest font-semibold">Title</th>
                <th className="px-6 py-3 text-[#45474c] text-xs uppercase tracking-widest font-semibold">Status</th>
                <th className="px-6 py-3 text-[#45474c] text-xs uppercase tracking-widest font-semibold">Category</th>
                <th className="px-6 py-3 text-[#45474c] text-xs uppercase tracking-widest font-semibold text-center">Likelihood</th>
                <th className="px-6 py-3 text-[#45474c] text-xs uppercase tracking-widest font-semibold text-center">Impact</th>
                <th className="px-6 py-3 text-[#45474c] text-xs uppercase tracking-widest font-semibold text-center">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {risks.map((risk) => (
                <tr key={risk.id} className="hover:bg-gray-50 transition cursor-pointer" onClick={() => router.push(`/dashboard/risks/${risk.id}`)}>
                  <td className="px-6 py-4 text-sm font-medium text-[#191c1f]">{risk.title}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${risk.status === 'Open' ? 'bg-blue-50 text-blue-700' : 'bg-gray-100 text-gray-700'}`}>
                      {risk.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-[#45474c]">{risk.category}</td>
                  <td className="px-6 py-4 text-sm text-[#45474c] text-center">{risk.likelihood}</td>
                  <td className="px-6 py-4 text-sm text-[#45474c] text-center">{risk.impact}</td>
                  <td className="px-6 py-4 text-sm text-center">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${risk.inherent_risk_score >= 10 ? 'bg-red-50 text-red-700' : 'bg-gray-100 text-gray-700'}`}>
                      {risk.inherent_risk_score}
                    </span>
                  </td>
                </tr>
              ))}
              {risks.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-[#45474c] text-sm">No risks found. Add one to get started.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
