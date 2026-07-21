import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  color: string;
  isDark: boolean;
}

export default function StatCard({
  title,
  value,
  icon: Icon,
  color,
  isDark
}: StatCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.2 }}
      className={`p-6 rounded-2xl border flex items-center justify-between hover:shadow-lg transition-all ${
        isDark 
          ? 'glass-card-dark border-white/5 hover:border-primary/20' 
          : 'glass-card-light border-gray-200 hover:border-primary/20'
      }`}
    >
      <div className="space-y-2">
        <span className={`text-xs font-semibold uppercase tracking-wider block ${
          isDark ? 'text-gray-400' : 'text-gray-500'
        }`}>
          {title}
        </span>
        <h4 className={`text-xl md:text-2xl font-black tracking-tight ${
          isDark ? 'text-white' : 'text-gray-900'
        }`}>
          {value}
        </h4>
      </div>

      <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${color} flex items-center justify-center text-white shadow-md`}>
        <Icon size={22} />
      </div>
    </motion.div>
  );
}
