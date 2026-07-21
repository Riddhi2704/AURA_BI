import type { ExecutiveSummary } from '../types';
import { motion } from 'framer-motion';
import { Landmark, Award, Signature } from 'lucide-react';

interface CEOPitchProps {
  pitchData: ExecutiveSummary;
  companyName: string;
  isDark: boolean;
}

export default function CEOPitch({ pitchData, companyName, isDark }: CEOPitchProps) {
  
  // Format the pitch paragraphs nicely
  const pitchParagraphs = pitchData.pitch.split('\n').filter(p => p.trim().length > 0);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={`max-w-3xl mx-auto p-8 md:p-12 rounded-2xl border shadow-xl relative ${
        isDark 
          ? 'bg-gradient-to-b from-gray-900 to-slate-950 border-white/10 text-gray-200' 
          : 'bg-white border-gray-200 text-gray-800'
      }`}
    >
      {/* Visual background accents */}
      <div className="absolute top-0 right-0 w-48 h-48 rounded-full bg-gradient-to-br from-primary/5 to-accent/5 blur-3xl pointer-events-none" />

      {/* Styled Corporate Letterhead */}
      <div className="border-b border-inherit pb-6 mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Landmark size={18} className="text-primary" />
            <span className="font-extrabold text-sm uppercase tracking-widest text-primary">
              AURA BI STRATEGIC LABS
            </span>
          </div>
          <span className="text-[10px] text-gray-400 dark:text-gray-500 uppercase tracking-widest">
            AI Transformation & Advisory Services
          </span>
        </div>

        <div className="text-left md:text-right text-xs text-gray-500 dark:text-gray-400">
          <div>Strategic Briefing Memo</div>
          <div>Ref: BI-REC-{companyName.toUpperCase().replace(/ /g, '-')}-01</div>
          <div>Date: {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</div>
        </div>
      </div>

      {/* Memo Fields */}
      <div className={`p-4 rounded-xl mb-8 space-y-1.5 text-xs ${
        isDark ? 'bg-white/5' : 'bg-gray-50'
      }`}>
        <div className="grid grid-cols-6">
          <span className="font-bold col-span-1 text-primary">TO:</span>
          <span className="col-span-5 font-semibold text-gray-900 dark:text-white">
            Chief Executive Officer, {companyName}
          </span>
        </div>
        <div className="grid grid-cols-6">
          <span className="font-bold col-span-1 text-primary">FROM:</span>
          <span className="col-span-5 font-semibold text-gray-900 dark:text-white">
            Principal AI Architect, AURA BISwarm
          </span>
        </div>
        <div className="grid grid-cols-6">
          <span className="font-bold col-span-1 text-primary">SUBJ:</span>
          <span className="col-span-5 font-bold text-accent">
            {pitchData.headline}
          </span>
        </div>
      </div>

      {/* Pitch Content paragraphs with typewriter entry */}
      <div className="space-y-5 text-sm leading-relaxed text-gray-700 dark:text-gray-300">
        {pitchParagraphs.map((para, index) => (
          <motion.p
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * index + 0.2 }}
          >
            {para}
          </motion.p>
        ))}
      </div>

      {/* Executive Sign-off Footer */}
      <div className="border-t border-inherit mt-10 pt-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
            <Signature size={18} />
          </div>
          <div>
            <div className={`font-bold text-xs ${isDark ? 'text-white' : 'text-gray-800'}`}>
              AURA Multi-Agent Swarm
            </div>
            <div className="text-[10px] text-gray-500">
              Autonomous Consulting Collective
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[10px] text-gray-400 uppercase tracking-widest border border-dashed border-inherit px-3 py-1.5 rounded-lg bg-inherit">
          <Award size={12} className="text-yellow-500" />
          <span>Verified AI Proposal</span>
        </div>
      </div>
    </motion.div>
  );
}
