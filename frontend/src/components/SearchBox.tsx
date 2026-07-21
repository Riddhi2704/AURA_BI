import React, { useState, useEffect } from 'react';
import { Search, Loader2, Sparkles, CheckCircle2, Circle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface SearchBoxProps {
  onSearch: (company: string) => void;
  isLoading: boolean;
  isDark: boolean;
}

export default function SearchBox({ onSearch, isLoading, isDark }: SearchBoxProps) {
  const [query, setQuery] = useState('');
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    { label: "1. Research Agent", desc: "Crawling company financials, headquarters, and executives" },
    { label: "2. News Agent", desc: "Scanning recent articles and corporate announcements" },
    { label: "3. Business Analyst Agent", desc: "Identifying bottlenecks, weaknesses, and SWOT factors" },
    { label: "4. Competitor Agent", desc: "Benchmarking core products and comparing market share" },
    { label: "5. AI Consultant Agent", desc: "Calculating ROI models and formulating technology paths" },
    { label: "6. CEO Pitch Agent", desc: "Drafting the executive summary and tailored CEO pitch" }
  ];

  // Rotate loading steps when loading is active to simulate progress
  useEffect(() => {
    if (!isLoading) {
      setActiveStep(0);
      return;
    }

    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 2200); // Progress roughly every 2.2 seconds to spread across a 13-second wait

    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      onSearch(trimmed);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4 z-10">
      <form onSubmit={handleSubmit} className="relative mb-6">
        <div className="relative flex items-center">
          <input
            type="text"
            placeholder="Enter company name (e.g. Stripe, Apple, Tesla)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            className={`w-full h-14 pl-12 pr-28 rounded-2xl border text-sm font-medium transition-all ${
              isDark 
                ? 'glass-input-dark' 
                : 'glass-input-light'
            }`}
          />
          <div className="absolute left-4 text-gray-400">
            <Search size={18} />
          </div>
          
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="absolute right-2 px-5 h-10 rounded-xl font-semibold text-xs text-white bg-gradient-to-r from-primary via-secondary to-accent hover:brightness-110 shadow transition-all disabled:opacity-40 flex items-center gap-1.5"
          >
            {isLoading ? (
              <>
                <Loader2 size={12} className="animate-spin" />
                <span>Searching</span>
              </>
            ) : (
              <>
                <Sparkles size={12} />
                <span>Analyze</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Stepper Agent Loading Sequence */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`p-6 rounded-2xl border text-left mb-8 ${
              isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'
            }`}
          >
            <div className="flex items-center gap-2 mb-4">
              <Loader2 size={16} className="animate-spin text-primary" />
              <h3 className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>
                Executing Multi-Agent Consulting Pipeline
              </h3>
            </div>
            
            <div className="space-y-4">
              {steps.map((step, index) => {
                const isCompleted = activeStep > index;
                const isActive = activeStep === index;
                
                return (
                  <div key={index} className="flex gap-3 items-start opacity-90">
                    <div className="mt-0.5 shrink-0">
                      {isCompleted ? (
                        <CheckCircle2 size={15} className="text-success" />
                      ) : isActive ? (
                        <Loader2 size={15} className="text-accent animate-spin" />
                      ) : (
                        <Circle size={15} className="text-gray-500" />
                      )}
                    </div>
                    
                    <div className="flex flex-col">
                      <span className={`text-xs font-semibold ${
                        isActive 
                          ? 'text-accent' 
                          : isCompleted 
                            ? 'text-success' 
                            : isDark ? 'text-gray-500' : 'text-gray-400'
                      }`}>
                        {step.label}
                      </span>
                      {isActive && (
                        <motion.span 
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className={`text-[10px] ${isDark ? 'text-gray-400' : 'text-gray-500'}`}
                        >
                          {step.desc}
                        </motion.span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
