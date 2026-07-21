import { 
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from 'recharts';
import { motion } from 'framer-motion';
import { LineChart, BarChart2, PieChart as PieIcon } from 'lucide-react';
import type { AIRecommendation, CompetitorRow } from '../types';

interface ChartCardProps {
  recommendations: AIRecommendation[];
  competitors: CompetitorRow[];
  isDark: boolean;
}

export default function ChartCard({
  recommendations,
  competitors,
  isDark
}: ChartCardProps) {
  
  // 1. Line Chart Data: Simulate 4 quarters revenue boost
  const areaData = [
    { name: 'Q1 Launch', baseline: 100, projection: 105 },
    { name: 'Q2 Deploy', baseline: 100, projection: 118 },
    { name: 'Q3 Optimize', baseline: 100, projection: 132 },
    { name: 'Q4 ROI Peak', baseline: 100, projection: 145 },
  ];

  // 2. Bar Chart Data: Convert estimated cost & ROI percentages into chart items
  const barData = recommendations.slice(0, 3).map((rec, i) => {
    // Parse values from string e.g. "$150k" -> 150
    const costMatch = rec.estimated_cost.replace(/[^0-9]/g, '');
    const cost = costMatch ? parseInt(costMatch) : 100;
    
    // Parse ROI percentage e.g. "250%" -> 250
    const roiMatch = rec.expected_roi.replace(/[^0-9]/g, '');
    const roiVal = roiMatch ? parseInt(roiMatch) : 200;
    
    return {
      name: `Rec ${i + 1}`,
      Cost: cost,
      ROIValue: Math.round(cost * (roiVal / 100))
    };
  });

  // 3. Pie Chart Data: Competitor distribution
  const pieData = competitors.map((c, idx) => {
    // Parse revenue: e.g. "$16.1 Billion" -> 16
    const revMatch = c.revenue.replace(/[^0-9.]/g, '');
    const val = revMatch ? parseFloat(revMatch) : 10 + idx * 5;
    return {
      name: c.name,
      value: val
    };
  });

  const COLORS = ['#6366F1', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B'];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Area Chart: Revenue Projection */}
      <motion.div
        whileHover={{ y: -2 }}
        className={`p-5 rounded-2xl border flex flex-col h-80 justify-between ${
          isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'
        }`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <LineChart size={16} className="text-primary" />
            <span className={`font-bold text-sm ${isDark ? 'text-white' : 'text-gray-800'}`}>
              Cumulative Performance Forecast
            </span>
          </div>
          <span className="text-[10px] text-gray-400">Quarterly index (%)</span>
        </div>
        <div className="flex-1 w-full text-[10px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={areaData}>
              <defs>
                <linearGradient id="colorProj" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="name" stroke={isDark ? "#4B5563" : "#9CA3AF"} />
              <YAxis stroke={isDark ? "#4B5563" : "#9CA3AF"} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: isDark ? '#111827' : '#ffffff', 
                  borderColor: isDark ? 'rgba(255, 255, 255, 0.1)' : '#e5e7eb',
                  color: isDark ? '#ffffff' : '#111827'
                }} 
              />
              <Area type="monotone" dataKey="projection" stroke="#6366F1" strokeWidth={2} fillOpacity={1} fill="url(#colorProj)" name="AI Projection" />
              <Area type="monotone" dataKey="baseline" stroke="#9CA3AF" strokeWidth={1} fillOpacity={0} strokeDasharray="5 5" name="Status Quo" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Bar Chart: Costs vs Savings */}
      <motion.div
        whileHover={{ y: -2 }}
        className={`p-5 rounded-2xl border flex flex-col h-80 justify-between ${
          isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'
        }`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BarChart2 size={16} className="text-secondary" />
            <span className={`font-bold text-sm ${isDark ? 'text-white' : 'text-gray-800'}`}>
              Cost vs. Expected Returns
            </span>
          </div>
          <span className="text-[10px] text-gray-400">Scale index (k$)</span>
        </div>
        <div className="flex-1 w-full text-[10px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData}>
              <XAxis dataKey="name" stroke={isDark ? "#4B5563" : "#9CA3AF"} />
              <YAxis stroke={isDark ? "#4B5563" : "#9CA3AF"} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: isDark ? '#111827' : '#ffffff', 
                  borderColor: isDark ? 'rgba(255, 255, 255, 0.1)' : '#e5e7eb',
                  color: isDark ? '#ffffff' : '#111827'
                }} 
              />
              <Legend verticalAlign="top" height={36} iconSize={8} />
              <Bar dataKey="Cost" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="Invested Cost" />
              <Bar dataKey="ROIValue" fill="#10B981" radius={[4, 4, 0, 0]} name="Expected ROI" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Pie Chart: Market Size benchmarks */}
      <motion.div
        whileHover={{ y: -2 }}
        className={`p-5 rounded-2xl border flex flex-col h-80 justify-between ${
          isDark ? 'glass-card-dark border-white/5' : 'glass-card-light border-gray-200'
        }`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <PieIcon size={16} className="text-accent" />
            <span className={`font-bold text-sm ${isDark ? 'text-white' : 'text-gray-800'}`}>
              Competitor Revenue Share
            </span>
          </div>
          <span className="text-[10px] text-gray-400">Volume distribution</span>
        </div>
        
        {pieData.length === 0 ? (
          <div className="flex-1 flex items-center justify-center text-xs text-gray-500 italic">
            Insufficient competitor comparison values.
          </div>
        ) : (
          <div className="flex-1 w-full flex items-center justify-center text-[10px]">
            <ResponsiveContainer width="100%" height="80%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: isDark ? '#111827' : '#ffffff', 
                    borderColor: isDark ? 'rgba(255, 255, 255, 0.1)' : '#e5e7eb',
                    color: isDark ? '#ffffff' : '#111827'
                  }} 
                />
                <Legend verticalAlign="bottom" height={36} iconSize={6} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </motion.div>
    </div>
  );
}
