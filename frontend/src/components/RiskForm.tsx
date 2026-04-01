"use client";

import { useEffect, useState } from "react";
import { createRisk, updateRisk, getRisk } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";

export default function RiskForm() {
  const params = useParams();
  const router = useRouter();
  const riskId = params.id as string;
  const isNew = riskId === "new";

  const [loading, setLoading] = useState(!isNew);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    threat_source: "",
    vulnerability: "",
    asset_at_risk: "",
    category: "Organisational",
    likelihood: 1,
    impact: 1,
  });

  useEffect(() => {
    if (!isNew) {
      async function fetchRisk() {
        try {
          const res = await getRisk(riskId);
          setFormData(res.data);
        } catch (error) {
          console.error("Failed to load risk", error);
        } finally {
          setLoading(false);
        }
      }
      fetchRisk();
    }
  }, [riskId, isNew]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isNew) {
        await createRisk(formData);
      } else {
        await updateRisk(riskId, formData);
      }
      router.push("/dashboard/risks");
    } catch (error) {
      console.error("Failed to save risk", error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="title" className="block text-sm font-medium leading-6 text-gray-900">Title</label>
        <div className="mt-2">
          <input
            type="text"
            name="title"
            id="title"
            required
            value={formData.title}
            onChange={handleChange}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
          />
        </div>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium leading-6 text-gray-900">Description</label>
        <div className="mt-2">
          <textarea
            id="description"
            name="description"
            rows={3}
            required
            value={formData.description}
            onChange={handleChange}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
        <div className="sm:col-span-2">
          <label htmlFor="threat_source" className="block text-sm font-medium leading-6 text-gray-900">Threat Source</label>
          <div className="mt-2">
            <input type="text" name="threat_source" id="threat_source" required value={formData.threat_source} onChange={handleChange} className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
          </div>
        </div>
        <div className="sm:col-span-2">
          <label htmlFor="vulnerability" className="block text-sm font-medium leading-6 text-gray-900">Vulnerability</label>
          <div className="mt-2">
            <input type="text" name="vulnerability" id="vulnerability" required value={formData.vulnerability} onChange={handleChange} className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
          </div>
        </div>
        <div className="sm:col-span-2">
          <label htmlFor="asset_at_risk" className="block text-sm font-medium leading-6 text-gray-900">Asset at Risk</label>
          <div className="mt-2">
            <input type="text" name="asset_at_risk" id="asset_at_risk" required value={formData.asset_at_risk} onChange={handleChange} className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
          </div>
        </div>

        <div className="sm:col-span-2">
          <label htmlFor="category" className="block text-sm font-medium leading-6 text-gray-900">Category</label>
          <div className="mt-2">
            <select id="category" name="category" value={formData.category} onChange={handleChange} className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
              <option>Organisational</option>
              <option>People</option>
              <option>Physical</option>
              <option>Technological</option>
            </select>
          </div>
        </div>

        <div className="sm:col-span-2">
          <label htmlFor="likelihood" className="block text-sm font-medium leading-6 text-gray-900">Likelihood (1-5)</label>
          <div className="mt-2">
            <select id="likelihood" name="likelihood" value={formData.likelihood} onChange={handleChange} className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
              {[1, 2, 3, 4, 5].map((val) => (<option key={val} value={val}>{val}</option>))}
            </select>
          </div>
        </div>

        <div className="sm:col-span-2">
          <label htmlFor="impact" className="block text-sm font-medium leading-6 text-gray-900">Impact (1-5)</label>
          <div className="mt-2">
            <select id="impact" name="impact" value={formData.impact} onChange={handleChange} className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
              {[1, 2, 3, 4, 5].map((val) => (<option key={val} value={val}>{val}</option>))}
            </select>
          </div>
        </div>
      </div>

      <div className="mt-6 flex items-center justify-end gap-x-6">
        <button type="button" onClick={() => router.push('/dashboard/risks')} className="text-sm font-semibold leading-6 text-gray-900">Cancel</button>
        <button type="submit" className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Save</button>
      </div>
    </form>
  );
}
