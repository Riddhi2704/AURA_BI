import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, Landmark, Users, DollarSign, Globe, 
  AlertTriangle, Lightbulb, ChevronRight,
  Newspaper, ArrowRight, CheckCircle2
} from 'lucide-react';

import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import SearchBox from './components/SearchBox';
import StatCard from './components/StatCard';
import CompetitorTable from './components/CompetitorTable';
import AIRecommendationCard from './components/AIRecommendationCard';
import CEOPitch from './components/CEOPitch';
import Timeline from './components/Timeline';
import ChartCard from './components/ChartCard';

import { searchCompany, getRecentSearches } from './services/api';
import type { BIReport } from './types';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<BIReport | null>(null);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [isDark, setIsDark] = useState(true);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Sync dark mode class
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  // Load search history on startup
  useEffect(() => {
    async function loadHistory() {
      const history = await getRecentSearches();
      setRecentSearches(history);
    }
    loadHistory();
  }, []);

  const handleSearch = async (companyName: string) => {
    setLoading(true);
    setSearchError(null);
    try {
      const data = await searchCompany(companyName);
      setReport(data);
      setActiveTab('dashboard'); // Route back to main dashboard
      
      // Reload history to capture new queries
      const history = await getRecentSearches();
      setRecentSearches(history);
    } catch (err: any) {
      console.error(err);
      setSearchError(err.message || 'Error occurred during agent analysis pipeline.');
    } finally {
      setLoading(false);
    }
  };

  const copyReportToClipboard = () => {
    if (!report) return;
    const md = `
# Business Intelligence & AI Recommendation Report: ${report.company_name}
Generated at: ${report.generated_at}

## 1. Company Overview
* Industry: ${report.overview.industry}
* Headquarters: ${report.overview.headquarters}
* Revenue: ${report.overview.revenue}
* Funding: ${report.overview.funding}

## 2. SWOT Analysis
### Strengths:
${report.swot.strengths.map(s => `- ${s}`).join('\n')}

### Weaknesses:
${report.swot.weaknesses.map(w => `- ${w}`).join('\n')}

### Opportunities:
${report.swot.opportunities.map(o => `- ${o}`).join('\n')}

### Threats:
${report.swot.threats.map(t => `- ${t}`).join('\n')}

## 3. Proposed AI Solutions
${report.ai_recommendations.map((rec, i) => `
### Recommendation ${i+1}: ${rec.recommended_solution}
* Problem: ${rec.problem}
* Evidence: ${rec.evidence}
* Reasoning: ${rec.reasoning}
* Expected Benefits: ${rec.expected_benefits}
* Difficulty: ${rec.implementation_difficulty}
* Cost: ${rec.estimated_cost}
* Timeline: ${rec.timeline}
* Expected ROI: ${rec.expected_roi}
* Priority: ${rec.priority}
`).join('\n')}

## 4. CEO Executive Pitch Memo
* Headline: ${report.executive_summary.headline}
* Summary: ${report.executive_summary.summary}

${report.executive_summary.pitch}
`;
    navigator.clipboard.writeText(md);
  };

  return (
    <div className={`flex w-screen h-screen overflow-hidden ${
      isDark ? 'bg-radial-grid-dark text-gray-200' : 'bg-radial-grid-light text-gray-800'
    }`}>
      {/* Sidebar navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        recentSearches={recentSearches}
        onSelectRecent={handleSearch}
        isDark={isDark}
        setIsDark={setIsDark}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
        hasReport={!!report}
      />

      {/* Main page content area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar report={report} isDark={isDark} onCopyText={copyReportToClipboard} />

        <main className="flex-1 overflow-y-auto px-6 py-8">
          {searchError && (
            <div className="max-w-xl mx-auto mb-6 p-4 rounded-xl border border-red-500/20 bg-red-950/20 text-red-400 text-xs text-center flex items-center justify-center gap-2">
              <AlertTriangle size={14} />
              <span>{searchError}</span>
            </div>
          )}

          {/* Search bar is shown at the top if a report is already loaded */}
          {report && !loading && (
            <div className="mb-8">
              <SearchBox onSearch={handleSearch} isLoading={loading} isDark={isDark} />
            </div>
          )}

          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                key="loading-box"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 flex flex-col items-center justify-center py-20"
              >
                <SearchBox onSearch={handleSearch} isLoading={loading} isDark={isDark} />
              </motion.div>
            ) : !report ? (
              <motion.div
                key="hero-box"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex-1 flex flex-col items-center"
              >
                <div className="w-full max-w-xl mb-6">
                  <SearchBox onSearch={handleSearch} isLoading={loading} isDark={isDark} />
                </div>
                <Hero isDark={isDark} onSearch={handleSearch} />
              </motion.div>
            ) : (
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                transition={{ duration: 0.3 }}
                className="space-y-8 max-w-7xl mx-auto pb-16"
              >
                {/* =======================================================
                    TAB 1: MAIN DASHBOARD VIEW
                    ======================================================= */}
                {activeTab === 'dashboard' && (
                  <>
                    {/* Header profile cards */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-inherit">
                      <div>
                        <h2 className={`text-2xl md:text-3xl font-extrabold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
                          {report.company_name} Dashboard
                        </h2>
                        <p className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                          Multi-agent strategic report compiled at: <span className="font-semibold text-accent">{report.generated_at}</span>
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${
                          isDark ? 'bg-white/5 border-white/10 text-gray-300' : 'bg-gray-100 border-gray-200 text-gray-700'
                        }`}>
                          Industry: {report.overview.industry}
                        </span>
                      </div>
                    </div>

                    {/* Stats cards Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                      <StatCard title="Revenue" value={report.overview.revenue} icon={DollarSign} color="from-blue-500 to-indigo-500" isDark={isDark} />
                      <StatCard title="Headquarters" value={report.overview.headquarters.split(',')[0]} icon={Landmark} color="from-purple-500 to-pink-500" isDark={isDark} />
                      <StatCard title="Funding Scale" value={report.overview.funding} icon={Users} color="from-emerald-500 to-teal-500" isDark={isDark} />
                      <StatCard title="Global Markets" value={report.overview.geographic_presence.length > 30 ? report.overview.geographic_presence.substring(0, 30) + '...' : report.overview.geographic_presence} icon={Globe} color="from-cyan-500 to-sky-500" isDark={isDark} />
                    </div>

                    {/* Performance Visual Charts */}
                    <ChartCard recommendations={report.ai_recommendations} competitors={report.competitors} isDark={isDark} />

                    {/* Main contents details */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      {/* Left: Summary and News */}
                      <div className="lg:col-span-2 space-y-6 text-left">
                        {/* Executive summary memo */}
                        <div className={`p-6 rounded-2xl border ${isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'}`}>
                          <h3 className={`font-bold text-sm mb-3 flex items-center gap-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>
                            <Sparkles size={16} className="text-primary animate-pulse" />
                            <span>Executive Summary Briefing</span>
                          </h3>
                          <p className={`text-xs font-semibold text-accent mb-3 uppercase tracking-wider`}>
                            {report.executive_summary.headline}
                          </p>
                          <p className={`text-xs leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                            {report.executive_summary.summary}
                          </p>
                        </div>

                        {/* Recent News feed card */}
                        <div className={`p-6 rounded-2xl border ${isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'}`}>
                          <h3 className={`font-bold text-sm mb-4 flex items-center gap-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>
                            <Newspaper size={16} className="text-accent" />
                            <span>Latest Corporate Intelligence & News</span>
                          </h3>
                          <div className="space-y-4">
                            {report.news.map((item, idx) => (
                              <div key={idx} className="p-4 rounded-xl bg-inherit border border-inherit hover:border-accent/40 transition-colors">
                                <div className="flex items-center justify-between gap-4 mb-2">
                                  <h4 className={`text-xs font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>
                                    {item.title}
                                  </h4>
                                  {item.date && (
                                    <span className="text-[9px] text-gray-500 shrink-0 font-semibold uppercase">
                                      {item.date}
                                    </span>
                                  )}
                                </div>
                                <p className={`text-[11px] leading-relaxed mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                                  {item.summary}
                                </p>
                                {item.url && (
                                  <a 
                                    href={item.url} 
                                    target="_blank" 
                                    rel="noreferrer"
                                    className="text-[10px] text-primary hover:text-accent font-semibold inline-flex items-center gap-0.5"
                                  >
                                    <span>Read Source</span>
                                    <ArrowRight size={10} />
                                  </a>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Right: Challenges, Executives, and Quick links */}
                      <div className="space-y-6 text-left">
                        {/* Leadership */}
                        <div className={`p-6 rounded-2xl border ${isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'}`}>
                          <h3 className={`font-bold text-sm mb-3 ${isDark ? 'text-white' : 'text-gray-800'}`}>
                            Key Corporate Leadership
                          </h3>
                          <ul className="space-y-2.5 text-xs">
                            {report.overview.key_executives.map((exe, i) => (
                              <li key={i} className="flex items-center justify-between py-1 border-b border-inherit last:border-0">
                                <span className={`font-semibold ${isDark ? 'text-gray-200' : 'text-gray-700'}`}>
                                  {exe.split(' (')[0]}
                                </span>
                                <span className="text-[10px] text-gray-500">
                                  {exe.includes('(') ? exe.split('(')[1].replace(')', '') : 'Executive'}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Challenges & Bottlenecks */}
                        <div className={`p-6 rounded-2xl border ${isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'}`}>
                          <h3 className={`font-bold text-sm mb-3 text-red-500 dark:text-red-400 flex items-center gap-1.5`}>
                            <AlertTriangle size={14} />
                            <span>Business Bottlenecks</span>
                          </h3>
                          <ul className="space-y-2 text-xs text-gray-400 dark:text-gray-300 pl-4 list-disc">
                            {report.overview.business_challenges.map((c, i) => (
                              <li key={i} className="leading-relaxed">{c}</li>
                            ))}
                          </ul>
                        </div>

                        {/* Quick Action Navigation links */}
                        <div className={`p-6 rounded-2xl border ${isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'}`}>
                          <h3 className={`font-bold text-sm mb-3 ${isDark ? 'text-white' : 'text-gray-800'}`}>
                            Strategic Sections
                          </h3>
                          <div className="flex flex-col gap-2">
                            <button 
                              onClick={() => setActiveTab('swot')}
                              className="w-full p-2.5 rounded-xl border border-inherit hover:border-primary/40 flex items-center justify-between text-xs transition-colors"
                            >
                              <span>View SWOT quadrants</span>
                              <ChevronRight size={14} className="text-primary" />
                            </button>
                            <button 
                              onClick={() => setActiveTab('competitors')}
                              className="w-full p-2.5 rounded-xl border border-inherit hover:border-primary/40 flex items-center justify-between text-xs transition-colors"
                            >
                              <span>View Competitor Benchmarking Matrix</span>
                              <ChevronRight size={14} className="text-primary" />
                            </button>
                            <button 
                              onClick={() => setActiveTab('ai_opportunities')}
                              className="w-full p-2.5 rounded-xl border border-inherit hover:border-primary/40 flex items-center justify-between text-xs transition-colors"
                            >
                              <span>View AI Implementation Roadmap</span>
                              <ChevronRight size={14} className="text-primary" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* =======================================================
                    TAB 2: DETAILED SWOT PAGE
                    ======================================================= */}
                {activeTab === 'swot' && (
                  <div className="space-y-6 text-left">
                    <div>
                      <h2 className={`text-2xl font-extrabold ${isDark ? 'text-white' : 'text-gray-950'}`}>
                        SWOT Quadrants Analysis
                      </h2>
                      <p className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Deep-dive strategic review detailing internal advantages vs external operational threats.
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Strengths */}
                      <div className={`p-6 rounded-2xl border ${
                        isDark ? 'glass-card-dark border-emerald-500/10' : 'bg-white border-emerald-500/20'
                      }`}>
                        <div className="flex items-center gap-2 mb-4 text-emerald-500 dark:text-emerald-400">
                          <CheckCircle2 size={20} />
                          <h3 className="font-extrabold text-base uppercase tracking-wider">Strengths</h3>
                        </div>
                        <ul className="space-y-3 text-xs pl-4 list-disc leading-relaxed text-gray-600 dark:text-gray-300">
                          {report.swot.strengths.map((item, idx) => <li key={idx}>{item}</li>)}
                        </ul>
                      </div>

                      {/* Weaknesses */}
                      <div className={`p-6 rounded-2xl border ${
                        isDark ? 'glass-card-dark border-red-500/10' : 'bg-white border-red-500/20'
                      }`}>
                        <div className="flex items-center gap-2 mb-4 text-red-500 dark:text-red-400">
                          <AlertTriangle size={20} />
                          <h3 className="font-extrabold text-base uppercase tracking-wider">Weaknesses</h3>
                        </div>
                        <ul className="space-y-3 text-xs pl-4 list-disc leading-relaxed text-gray-600 dark:text-gray-300">
                          {report.swot.weaknesses.map((item, idx) => <li key={idx}>{item}</li>)}
                        </ul>
                      </div>

                      {/* Opportunities */}
                      <div className={`p-6 rounded-2xl border ${
                        isDark ? 'glass-card-dark border-indigo-500/10' : 'bg-white border-indigo-500/20'
                      }`}>
                        <div className="flex items-center gap-2 mb-4 text-indigo-500 dark:text-indigo-400">
                          <Lightbulb size={20} />
                          <h3 className="font-extrabold text-base uppercase tracking-wider">Opportunities</h3>
                        </div>
                        <ul className="space-y-3 text-xs pl-4 list-disc leading-relaxed text-gray-600 dark:text-gray-300">
                          {report.swot.opportunities.map((item, idx) => <li key={idx}>{item}</li>)}
                        </ul>
                      </div>

                      {/* Threats */}
                      <div className={`p-6 rounded-2xl border ${
                        isDark ? 'glass-card-dark border-orange-500/10' : 'bg-white border-orange-500/20'
                      }`}>
                        <div className="flex items-center gap-2 mb-4 text-orange-500 dark:text-orange-400">
                          <AlertTriangle size={20} />
                          <h3 className="font-extrabold text-base uppercase tracking-wider">Threats</h3>
                        </div>
                        <ul className="space-y-3 text-xs pl-4 list-disc leading-relaxed text-gray-600 dark:text-gray-300">
                          {report.swot.threats.map((item, idx) => <li key={idx}>{item}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* =======================================================
                    TAB 3: COMPETITORS MATRIX PAGE
                    ======================================================= */}
                {activeTab === 'competitors' && (
                  <div className="space-y-6 text-left">
                    <div>
                      <h2 className={`text-2xl font-extrabold ${isDark ? 'text-white' : 'text-gray-950'}`}>
                        Competitor Comparison landscape
                      </h2>
                      <p className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Structured comparative intelligence showing how {report.company_name} ranks relative to top sector peers.
                      </p>
                    </div>

                    <CompetitorTable
                      competitors={report.competitors}
                      companyName={report.company_name}
                      subjectRevenue={report.overview.revenue}
                      isDark={isDark}
                    />
                  </div>
                )}

                {/* =======================================================
                    TAB 4: AI STRATEGIST ROADMAP PAGE
                    ======================================================= */}
                {activeTab === 'ai_opportunities' && (
                  <div className="space-y-8 text-left">
                    <div>
                      <h2 className={`text-2xl font-extrabold ${isDark ? 'text-white' : 'text-gray-950'}`}>
                        AI Transformation Consultant
                      </h2>
                      <p className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        ROI-modeled technology recommendations focused on operational bottlenecks and client automation.
                      </p>
                    </div>

                    {/* Timeline Gantt visualization */}
                    <Timeline recommendations={report.ai_recommendations} isDark={isDark} />

                    {/* Detailed Cards list */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {report.ai_recommendations.map((rec, index) => (
                        <AIRecommendationCard
                          key={index}
                          recommendation={rec}
                          index={index}
                          isDark={isDark}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* =======================================================
                    TAB 5: CEO PITCH MEMO PAGE
                    ======================================================= */}
                {activeTab === 'ceo_pitch' && (
                  <div className="space-y-6 text-left">
                    <div>
                      <h2 className={`text-2xl font-extrabold ${isDark ? 'text-white' : 'text-gray-950'}`}>
                        Personalized CEO Pitch Brief
                      </h2>
                      <p className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        Persuasive advisory memo framed in professional business language to initiate AI transformation collaboration.
                      </p>
                    </div>

                    <CEOPitch
                      pitchData={report.executive_summary}
                      companyName={report.company_name}
                      isDark={isDark}
                    />
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* Footer */}
        <footer className={`py-4 px-6 text-center text-[10px] border-t shrink-0 select-none ${
          isDark ? 'bg-background-dark/50 border-white/5 text-gray-500' : 'bg-gray-50 border-gray-100 text-gray-400'
        }`}>
          © {new Date().getFullYear()} AURA Business Intelligence swarms. Styled premium corporate consulting SaaS. All rights reserved.
        </footer>
      </div>
    </div>
  );
}
