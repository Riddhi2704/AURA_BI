import type { CompetitorRow } from '../types';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

interface CompetitorTableProps {
  competitors: CompetitorRow[];
  companyName: string;
  subjectRevenue: string;
  isDark: boolean;
}

export default function CompetitorTable({
  competitors,
  companyName,
  subjectRevenue,
  isDark
}: CompetitorTableProps) {
  
  // Combine subject company and competitors for direct visual side-by-side
  const allRows = [
    {
      name: `${companyName} (Subject)`,
      revenue: subjectRevenue,
      employees: "Target Company",
      presence: "See Profile",
      products: ["Core Platform Services"],
      technology: ["AI & Cloud Integrations"],
      strengths: ["Subject Company"],
      weaknesses: ["Subject Company"],
      market_position: "Leader",
      isSubject: true
    },
    ...competitors.map(c => ({ ...c, isSubject: false }))
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl border overflow-hidden ${
        isDark ? 'glass-card-dark border-white/10' : 'glass-card-light border-gray-200'
      }`}
    >
      <div className="p-5 border-b border-inherit flex items-center justify-between">
        <div>
          <h3 className={`font-bold text-base ${isDark ? 'text-white' : 'text-gray-800'}`}>
            Competitor Benchmarking Matrix
          </h3>
          <p className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            Side-by-side comparison of market size, geographic footprint, technology stack, and relative SWOT profiles.
          </p>
        </div>
        <div className={`px-2 py-1 rounded-md text-[10px] font-semibold border flex items-center gap-1 ${
          isDark ? 'bg-primary/10 border-primary/20 text-indigo-300' : 'bg-primary/5 border-primary/10 text-primary'
        }`}>
          <Sparkles size={10} />
          <span>Market Matrix</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className={`border-b border-inherit ${
              isDark ? 'bg-white/5 text-gray-400' : 'bg-gray-50 text-gray-500'
            }`}>
              <th className="p-4 font-semibold">Company</th>
              <th className="p-4 font-semibold">Revenue</th>
              <th className="p-4 font-semibold">Employees</th>
              <th className="p-4 font-semibold">Presence</th>
              <th className="p-4 font-semibold">Market Position</th>
              <th className="p-4 font-semibold">Products</th>
              <th className="p-4 font-semibold">Technology Stack</th>
              <th className="p-4 font-semibold">Key Strengths</th>
              <th className="p-4 font-semibold">Key Weaknesses</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-inherit">
            {allRows.map((row, index) => (
              <tr 
                key={index}
                className={`transition-colors ${
                  row.isSubject
                    ? isDark 
                      ? 'bg-primary/15 hover:bg-primary/20' 
                      : 'bg-indigo-50/60 hover:bg-indigo-50'
                    : isDark 
                      ? 'hover:bg-white/5' 
                      : 'hover:bg-gray-50/50'
                }`}
              >
                <td className="p-4 font-bold shrink-0">
                  <div className="flex flex-col">
                    <span className={isDark ? 'text-white' : 'text-gray-900'}>{row.name}</span>
                    {row.isSubject && (
                      <span className="text-[9px] text-primary uppercase font-bold tracking-wider mt-0.5">
                        Analysis Target
                      </span>
                    )}
                  </div>
                </td>
                <td className="p-4 whitespace-nowrap font-medium text-accent">{row.revenue}</td>
                <td className="p-4 whitespace-nowrap text-gray-400 dark:text-gray-300">{row.employees}</td>
                <td className="p-4 text-gray-400 dark:text-gray-300">{row.presence}</td>
                <td className="p-4">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                    row.market_position === 'Leader'
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                      : row.market_position === 'Challenger'
                        ? 'bg-sky-500/10 border-sky-500/20 text-sky-400'
                        : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                  }`}>
                    {row.market_position}
                  </span>
                </td>
                <td className="p-4 max-w-[150px]">
                  <div className="flex flex-wrap gap-1">
                    {row.products.map((p, i) => (
                      <span key={i} className={`px-1.5 py-0.5 rounded text-[9px] ${
                        isDark ? 'bg-white/5 text-gray-300' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {p}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="p-4 max-w-[150px]">
                  <div className="flex flex-wrap gap-1">
                    {row.technology.map((t, i) => (
                      <span key={i} className={`px-1.5 py-0.5 rounded text-[9px] ${
                        isDark ? 'bg-white/5 text-gray-300' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {t}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="p-4 max-w-[180px]">
                  <ul className="list-disc pl-3.5 space-y-0.5 text-gray-400 dark:text-gray-300">
                    {row.strengths.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </td>
                <td className="p-4 max-w-[180px]">
                  <ul className="list-disc pl-3.5 space-y-0.5 text-gray-400 dark:text-gray-300">
                    {row.weaknesses.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
