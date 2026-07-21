import { motion } from 'framer-motion';
import { Sparkles, BrainCircuit, LineChart, FileSpreadsheet, ShieldAlert, Cpu } from 'lucide-react';

interface HeroProps {
  isDark: boolean;
  onSearch: (company: string) => void;
}

export default function Hero({ isDark, onSearch }: HeroProps) {
  const containerVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        staggerChildren: 0.15
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const sampleCompanies = ["Stripe", "Tesla", "Nvidia", "Apple", "SpaceX"];

  const agentHighlights = [
    { title: "Research Agent", desc: "Crawls financial stats, leadership teams, products and strategic operations.", icon: Cpu, color: "from-blue-500 to-indigo-500" },
    { title: "News Analyst", desc: "Crawls recent product launches, partnerships, and market expansions.", icon: Sparkles, color: "from-purple-500 to-pink-500" },
    { title: "Business Analyst", desc: "Synthesizes operational bottlenecks and evaluates strategic SWOT profiles.", icon: ShieldAlert, color: "from-red-500 to-orange-500" },
    { title: "Competitor Agent", desc: "Builds a structured landscape matrix comparing features and market positions.", icon: FileSpreadsheet, color: "from-yellow-500 to-amber-500" },
    { title: "AI Consultant", desc: "Proposes technical integrations, estimating difficulty, costs, and timeline.", icon: BrainCircuit, color: "from-emerald-500 to-teal-500" },
    { title: "CEO Pitch Writer", desc: "Drafts a compelling, personalized executive brief tailored for C-suite engagement.", icon: LineChart, color: "from-cyan-500 to-sky-500" },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex-1 flex flex-col items-center justify-center max-w-5xl mx-auto px-6 py-12 text-center"
    >
      {/* Visual Badge */}
      <motion.div
        variants={itemVariants}
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold mb-6 border transition-all ${
          isDark 
            ? 'bg-primary/10 border-primary/20 text-indigo-300' 
            : 'bg-primary/5 border-primary/10 text-primary'
        }`}
      >
        <Sparkles size={12} className="animate-spin-slow" />
        <span>Enterprise Multi-Agent Platform</span>
      </motion.div>

      {/* Main Headers */}
      <motion.h1
        variants={itemVariants}
        className={`text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6 leading-tight ${
          isDark ? 'text-white' : 'text-gray-900'
        }`}
      >
        Automated Business Research &{' '}
        <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
          AI Consultant
        </span>
      </motion.h1>

      <motion.p
        variants={itemVariants}
        className={`text-base md:text-lg max-w-2xl mb-8 leading-relaxed ${
          isDark ? 'text-gray-400' : 'text-gray-600'
        }`}
      >
        Enter any company name below. Our specialized AI agent swarm will immediately browse the web, analyze financials, build SWOT matrices, benchmark competitors, and propose high-ROI AI transformation roadmaps.
      </motion.p>

      {/* Quick Start tags */}
      <motion.div
        variants={itemVariants}
        className="flex flex-wrap items-center justify-center gap-2.5 mb-16 text-xs"
      >
        <span className={isDark ? 'text-gray-500' : 'text-gray-400'}>Try searching:</span>
        {sampleCompanies.map((company) => (
          <button
            key={company}
            onClick={() => onSearch(company)}
            className={`px-3 py-1.5 rounded-lg border font-medium transition-all ${
              isDark 
                ? 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-primary/50 text-gray-300' 
                : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-primary/50 text-gray-700'
            }`}
          >
            {company}
          </button>
        ))}
      </motion.div>

      {/* Agent swarms overview grid */}
      <motion.div variants={itemVariants} className="w-full">
        <h2 className={`text-xl font-bold mb-6 text-left ${isDark ? 'text-white' : 'text-gray-800'}`}>
          Meet Your Multi-Agent Intelligence Swarm
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {agentHighlights.map((agent, index) => {
            const Icon = agent.icon;
            return (
              <motion.div
                key={index}
                whileHover={{ y: -4, rotateX: 2 }}
                className={`p-5 text-left rounded-2xl border transition-all ${
                  isDark 
                    ? 'glass-card-dark border-white/5 hover:border-white/10' 
                    : 'glass-card-light border-gray-200/50 hover:border-primary/20'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${agent.color} flex items-center justify-center text-white mb-4 shadow`}>
                  <Icon size={20} />
                </div>
                <h3 className={`font-semibold text-sm mb-2 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                  {agent.title}
                </h3>
                <p className={`text-xs leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  {agent.desc}
                </p>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </motion.div>
  );
}
