import type { AIRecommendation } from '../types';
import { motion } from 'framer-motion';
import { Brain, DollarSign, Clock, TrendingUp, AlertCircle, FileText, CheckCircle } from 'lucide-react';

interface AIRecommendationCardProps {
  recommendation: AIRecommendation;
  index: number;
  isDark: boolean;
}

export default function AIRecommendationCard({
  recommendation,
  index,
  isDark
}: AIRecommendationCardProps) {
  
  const getDifficultyColor = (diff: string) => {
    switch (diff.toLowerCase()) {
      case 'low': return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400';
      case 'medium': return 'bg-amber-500/10 border-amber-500/20 text-amber-400';
      case 'high': return 'bg-red-500/10 border-red-500/20 text-red-400';
      default: return 'bg-gray-500/10 border-gray-500/20 text-gray-400';
    }
  };

  const getPriorityColor = (prio: string) => {
    switch (prio.toLowerCase()) {
      case 'high': return 'bg-red-600/15 border-red-600/30 text-red-400';
      case 'medium': return 'bg-amber-500/15 border-amber-500/30 text-amber-400';
      case 'low': return 'bg-blue-500/15 border-blue-500/30 text-blue-400';
      default: return 'bg-gray-500/15 border-gray-500/30 text-gray-400';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`p-6 rounded-2xl border flex flex-col justify-between hover:shadow-xl transition-all relative overflow-hidden group ${
        isDark 
          ? 'glass-card-dark border-white/5 hover:border-primary/20' 
          : 'glass-card-light border-gray-200 hover:border-primary/30'
      }`}
    >
      {/* Decorative gradient light corner */}
      <div className="absolute -top-16 -right-16 w-32 h-32 rounded-full bg-gradient-to-br from-primary/10 to-accent/10 blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Header section */}
      <div>
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
              <Brain size={16} />
            </div>
            <span className={`text-xs font-bold ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              INITIATIVE #{index + 1}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${getDifficultyColor(recommendation.implementation_difficulty)}`}>
              Diff: {recommendation.implementation_difficulty}
            </span>
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${getPriorityColor(recommendation.priority)}`}>
              Priority: {recommendation.priority}
            </span>
          </div>
        </div>

        {/* Title */}
        <h4 className={`text-lg font-bold mb-5 ${isDark ? 'text-white' : 'text-gray-800'}`}>
          {recommendation.recommended_solution}
        </h4>

        {/* Problem, Evidence, Reasoning Columns */}
        <div className="space-y-4 text-xs mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 border-t border-b border-inherit py-4">
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-danger dark:text-red-400 uppercase tracking-wider text-[10px]">
                <AlertCircle size={12} />
                <span>Problem</span>
              </div>
              <p className={`leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                {recommendation.problem}
              </p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-accent uppercase tracking-wider text-[10px]">
                <FileText size={12} />
                <span>Evidence</span>
              </div>
              <p className={`leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                {recommendation.evidence}
              </p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-primary uppercase tracking-wider text-[10px]">
                <CheckCircle size={12} />
                <span>Reasoning</span>
              </div>
              <p className={`leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                {recommendation.reasoning}
              </p>
            </div>
          </div>

          <div className="space-y-1.5 bg-gradient-to-r from-primary/5 to-transparent p-3 rounded-lg border border-primary/10">
            <span className="font-bold text-[10px] text-primary uppercase tracking-wider block">
              Expected Benefits
            </span>
            <p className={`text-xs leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-700'}`}>
              {recommendation.expected_benefits}
            </p>
          </div>
        </div>
      </div>

      {/* Financials & Timeline Bottom Panel */}
      <div className={`grid grid-cols-3 gap-2 p-3 rounded-xl border text-center ${
        isDark ? 'bg-white/5 border-white/5' : 'bg-gray-50 border-gray-100'
      }`}>
        <div className="flex flex-col items-center justify-center py-1">
          <div className="flex items-center gap-1 text-xs font-semibold text-accent mb-0.5">
            <DollarSign size={13} />
            <span>Est. Cost</span>
          </div>
          <span className={`text-[11px] font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>
            {recommendation.estimated_cost}
          </span>
        </div>

        <div className="flex flex-col items-center justify-center py-1 border-l border-r border-inherit">
          <div className="flex items-center gap-1 text-xs font-semibold text-primary mb-0.5">
            <Clock size={13} />
            <span>Timeline</span>
          </div>
          <span className={`text-[11px] font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>
            {recommendation.timeline}
          </span>
        </div>

        <div className="flex flex-col items-center justify-center py-1">
          <div className="flex items-center gap-1 text-xs font-semibold text-success mb-0.5">
            <TrendingUp size={13} />
            <span>ROI</span>
          </div>
          <span className={`text-[11px] font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>
            {recommendation.expected_roi}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
