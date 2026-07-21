import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, Scale, Users2, BrainCircuit, Mail, 
  History, ChevronLeft, ChevronRight, Sun, Moon, Sparkles
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  recentSearches: string[];
  onSelectRecent: (company: string) => void;
  isDark: boolean;
  setIsDark: (dark: boolean) => void;
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
  hasReport: boolean;
}

export default function Sidebar({
  activeTab,
  setActiveTab,
  recentSearches,
  onSelectRecent,
  isDark,
  setIsDark,
  isCollapsed,
  setIsCollapsed,
  hasReport
}: SidebarProps) {
  
  const navItems = [
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard, requiresReport: false },
    { id: 'swot', name: 'SWOT Analysis', icon: Scale, requiresReport: true },
    { id: 'competitors', name: 'Competitors', icon: Users2, requiresReport: true },
    { id: 'ai_opportunities', name: 'AI Consultant', icon: BrainCircuit, requiresReport: true },
    { id: 'ceo_pitch', name: 'CEO Pitch Memo', icon: Mail, requiresReport: true },
  ];

  const sidebarVariants = {
    expanded: { width: '260px' },
    collapsed: { width: '70px' }
  };

  return (
    <motion.aside
      initial="expanded"
      animate={isCollapsed ? 'collapsed' : 'expanded'}
      variants={sidebarVariants}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className={`relative h-screen flex flex-col border-r shrink-0 z-20 ${
        isDark 
          ? 'glass-card-dark border-white/10 text-gray-200' 
          : 'glass-card-light border-gray-200 text-gray-800'
      }`}
    >
      {/* Collapse Trigger Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className={`absolute -right-3 top-8 flex items-center justify-center w-6 h-6 rounded-full border shadow-md transition-all ${
          isDark 
            ? 'bg-gray-800 border-white/10 hover:bg-gray-700 text-white' 
            : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-700'
        }`}
      >
        {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>

      {/* Brand Logo */}
      <div className="p-5 flex items-center gap-3 border-b border-inherit">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-tr from-primary to-accent text-white shadow-lg shrink-0">
          <Sparkles size={20} className="animate-pulse" />
        </div>
        <AnimatePresence>
          {!isCollapsed && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="font-bold text-lg bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent truncate"
            >
              AURA BI
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isDisabled = item.requiresReport && !hasReport;
          const isActive = activeTab === item.id;
          
          return (
            <button
              key={item.id}
              disabled={isDisabled}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative ${
                isActive
                  ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-md'
                  : isDisabled
                    ? 'opacity-40 cursor-not-allowed'
                    : isDark 
                      ? 'hover:bg-white/5 text-gray-400 hover:text-white' 
                      : 'hover:bg-gray-100 text-gray-600 hover:text-black'
              }`}
            >
              <Icon size={18} className={isActive ? '' : 'group-hover:scale-110 transition-transform'} />
              
              {!isCollapsed && (
                <span className="text-sm font-medium transition-opacity duration-200">
                  {item.name}
                </span>
              )}

              {/* Tooltip for collapsed view */}
              {isCollapsed && (
                <div className="absolute left-16 scale-0 group-hover:scale-100 transition-all rounded-md px-2.5 py-1 text-xs bg-gray-900 text-white z-30 pointer-events-none whitespace-nowrap shadow-xl border border-white/10">
                  {item.name} {isDisabled && '(Requires Search)'}
                </div>
              )}
            </button>
          );
        })}

        {/* History Divider */}
        <div className="border-t border-inherit my-4 pt-4">
          <div className="px-3 pb-2 flex items-center gap-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            <History size={12} />
            {!isCollapsed && <span>Recent Searches</span>}
          </div>
          
          <div className="space-y-1">
            {recentSearches.length === 0 ? (
              !isCollapsed && (
                <span className="px-3 text-xs text-gray-500 italic block">
                  No searches yet
                </span>
              )
            ) : (
              recentSearches.map((company, index) => (
                <button
                  key={index}
                  onClick={() => onSelectRecent(company)}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-xs truncate transition-colors ${
                    isDark 
                      ? 'text-gray-400 hover:bg-white/5 hover:text-white' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-black'
                  }`}
                  title={company}
                >
                  {isCollapsed ? company.charAt(0).toUpperCase() : company}
                </button>
              ))
            )}
          </div>
        </div>
      </nav>

      {/* Footer / Theme Toggle */}
      <div className="p-4 border-t border-inherit flex items-center justify-between gap-2 shrink-0">
        {!isCollapsed && (
          <span className="text-xs font-medium text-gray-500">
            {isDark ? 'Dark Mode' : 'Light Mode'}
          </span>
        )}
        <button
          onClick={() => setIsDark(!isDark)}
          className={`flex items-center justify-center w-9 h-9 rounded-xl transition-all ${
            isDark 
              ? 'bg-white/5 border border-white/10 hover:bg-white/10 text-yellow-400' 
              : 'bg-gray-100 border border-gray-200 hover:bg-gray-200 text-purple-600'
          }`}
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </motion.aside>
  );
}
