export interface CompanyOverview {
  name: string;
  industry: string;
  headquarters: string;
  geographic_presence: string;
  products_services: string[];
  revenue: string;
  funding: string;
  key_executives: string[];
  expansion_plans: string[];
  business_challenges: string[];
  risks: string[];
}

export interface NewsItem {
  title: string;
  url?: string;
  summary: string;
  date?: string;
}

export interface SWOTAnalysis {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface CompetitorRow {
  name: string;
  revenue: string;
  employees: string;
  presence: string;
  products: string[];
  technology: string[];
  strengths: string[];
  weaknesses: string[];
  market_position: string;
}

export interface AIRecommendation {
  problem: string;
  evidence: string;
  reasoning: string;
  recommended_solution: string;
  expected_benefits: string;
  implementation_difficulty: string;
  estimated_cost: string;
  timeline: string;
  expected_roi: string;
  priority: string;
}

export interface ExecutiveSummary {
  headline: string;
  summary: string;
  pitch: string;
}

export interface BIReport {
  company_name: string;
  overview: CompanyOverview;
  news: NewsItem[];
  swot: SWOTAnalysis;
  competitors: CompetitorRow[];
  ai_recommendations: AIRecommendation[];
  executive_summary: ExecutiveSummary;
  generated_at: string;
}
