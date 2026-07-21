import type { AIRecommendation } from '../types';
import { motion } from 'framer-motion';
import { Calendar, Activity } from 'lucide-react';

interface TimelineProps {
  recommendations: AIRecommendation[];
  isDark: boolean;
}

export default function Timeline({ recommendations, isDark }: TimelineProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className={`p-6 rounded-2xl border ${
        isDark ? 'glass-card-dark border-white/10' : 'glass-card-light border-gray-200'
      }`}
    >
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-inherit">
        <div className="flex items-center gap-2">
          <Calendar size={18} className="text-primary animate-pulse" />
          <h3 className={`font-bold text-base ${isDark ? 'text-white' : 'text-gray-800'}`}>
            Implementation Roadmap & Phases
          </h3>
        </div>
        <div className="flex items-center gap-4 text-[10px] text-gray-500 font-semibold uppercase tracking-wider">
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded bg-primary shrink-0" />
            <span>Phasing</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded bg-accent shrink-0" />
            <span>Milestones</span>
          </div>
        </div>
      </div>

      <div className="relative pl-6 space-y-8 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-[2px] before:bg-gradient-to-b before:from-primary before:via-secondary before:to-accent">
        {recommendations.map((rec, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.15 }}
            className="relative"
          >
            {/* Timeline Circle Bullet */}
            <div className="absolute -left-[23px] top-1 flex items-center justify-center w-4.5 h-4.5 rounded-full bg-slate-900 border-2 border-primary z-10 text-[9px] font-bold text-white bg-radial-grid-dark">
              {index + 1}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-start">
              {/* Left Column: Solution & Details */}
              <div className="lg:col-span-1">
                <h4 className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>
                  {rec.recommended_solution}
                </h4>
                <div className="flex items-center gap-2 mt-2 text-[10px]">
                  <span className="text-gray-400">Timeline:</span>
                  <span className="font-bold text-accent">{rec.timeline}</span>
                </div>
              </div>

              {/* Middle Column: Gantt Visual Bar */}
              <div className="lg:col-span-2 py-2">
                <div className={`h-3 rounded-full w-full relative overflow-hidden ${
                  isDark ? 'bg-white/5' : 'bg-gray-100'
                }`}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(index + 1) * 33}%` }}
                    transition={{ duration: 1, delay: 0.3 }}
                    className={`h-full rounded-full bg-gradient-to-r ${
                      index === 0 
                        ? 'from-primary to-indigo-500' 
                        : index === 1 
                          ? 'from-indigo-500 to-secondary' 
                          : 'from-secondary to-accent'
                    }`}
                  />
                </div>
                <div className="flex justify-between text-[8px] text-gray-500 mt-1.5 uppercase tracking-widest">
                  <span>Q1 Launch</span>
                  <span>Q2 Execution</span>
                  <span>Q3 Optimization</span>
                  <span>Q4 ROI Peak</span>
                </div>
              </div>

              {/* Right Column: Outcomes */}
              <div className={`lg:col-span-1 p-3 rounded-xl border flex flex-col justify-center text-xs ${
                isDark ? 'bg-white/5 border-white/5' : 'bg-gray-50 border-gray-100'
              }`}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-gray-400 font-medium">Est. Cost:</span>
                  <span className={`font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>{rec.estimated_cost}</span>
                </div>
                <div className="flex items-center justify-between border-t border-inherit pt-1.5">
                  <span className="text-success font-semibold flex items-center gap-1">
                    <Activity size={10} />
                    <span>Projected ROI:</span>
                  </span>
                  <span className="font-bold text-success">{rec.expected_roi}</span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
