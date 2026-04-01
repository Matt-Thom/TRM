import RiskTable from "@/components/RiskTable";
import Link from "next/link";

export default function RisksPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold leading-tight text-gray-900">
          Risk Register
        </h1>
        <Link
          href="/dashboard/risks/new"
          className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          Add Risk
        </Link>
      </div>

      <div className="bg-white p-6 shadow sm:rounded-lg">
        <RiskTable />
      </div>
    </div>
  );
}
