"use client";

import { useEffect, useState } from "react";
import { getRisks, getRiskMatrix } from "@/lib/api";
import Link from "next/link";

export default function RiskTable() {
  const [risks, setRisks] = useState<any[]>([]);
  const [matrix, setMatrix] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [risksData, matrixData] = await Promise.all([
          getRisks(),
          getRiskMatrix()
        ]);
        setRisks(risksData.data.items || []);
        setMatrix(matrixData.data);
      } catch (error) {
        console.error("Failed to fetch risk data:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getScoreColor = (score: number) => {
    if (!matrix) return "bg-gray-100 text-gray-800";
    const thresholds = matrix.thresholds;
    if (score >= thresholds.Critical.min) return "bg-red-100 text-red-800";
    if (score >= thresholds.High.min) return "bg-orange-100 text-orange-800";
    if (score >= thresholds.Medium.min) return "bg-yellow-100 text-yellow-800";
    return "bg-green-100 text-green-800";
  };

  if (loading) return <div>Loading risks...</div>;
  if (!risks.length) return <div>No risks found. Add one to get started.</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Title</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Score</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Owner</th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Last Updated</th>
            <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
              <span className="sr-only">Edit</span>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {risks.map((risk) => (
            <tr key={risk.id} className="hover:bg-gray-50">
              <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{risk.title}</td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{risk.category}</td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                <span className="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-gray-500/10">
                  {risk.status}
                </span>
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${getScoreColor(risk.inherent_risk_score)}`}>
                  {risk.inherent_risk_score}
                </span>
              </td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{risk.owner || "Unassigned"}</td>
              <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{new Date(risk.updated_at).toLocaleDateString()}</td>
              <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                <Link href={`/dashboard/risks/${risk.id}`} className="text-indigo-600 hover:text-indigo-900">
                  Edit<span className="sr-only">, {risk.title}</span>
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
