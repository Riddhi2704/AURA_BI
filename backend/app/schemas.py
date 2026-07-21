from pydantic import BaseModel, Field
from typing import List, Optional

class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(description="Internal strengths of the company")
    weaknesses: List[str] = Field(description="Internal weaknesses or bottlenecks of the company")
    opportunities: List[str] = Field(description="External growth or digital transformation opportunities")
    threats: List[str] = Field(description="External threats, market challenges, or regulatory risks")

class CompetitorRow(BaseModel):
    name: str = Field(description="Name of the competitor")
    revenue: str = Field(description="Competitor estimated revenue")
    employees: str = Field(description="Competitor estimated employee count")
    presence: str = Field(description="Geographic presence or core markets")
    products: List[str] = Field(description="Key products & services offered")
    technology: List[str] = Field(description="Core technologies used")
    strengths: List[str] = Field(description="Competitor's major strengths")
    weaknesses: List[str] = Field(description="Competitor's major weaknesses")
    market_position: str = Field(description="Market standing (e.g. Leader, Challenger, Niche)")

class AIRecommendation(BaseModel):
    problem: str = Field(description="Specific operational bottleneck or customer pain point identified")
    evidence: str = Field(description="Citable search evidence, news development, or metrics backing this problem")
    reasoning: str = Field(description="Logical explanation of why this problem exists and how AI resolves it")
    recommended_solution: str = Field(description="Specific AI/ML technology or product solution proposed")
    expected_benefits: str = Field(description="Tangible outcomes (e.g. cost savings, efficiency gains)")
    implementation_difficulty: str = Field(description="Low, Medium, or High implementation difficulty")
    estimated_cost: str = Field(description="Estimated cost range (e.g. $50k - $100k)")
    timeline: str = Field(description="Expected time to launch (e.g. 3-6 months)")
    expected_roi: str = Field(description="Expected return on investment (percentage or scale)")
    priority: str = Field(description="High, Medium, or Low urgency priority level")

class NewsItem(BaseModel):
    title: str = Field(description="News headline")
    url: Optional[str] = Field(None, description="Source URL if available")
    summary: str = Field(description="Brief summary of the news and business impact")
    date: Optional[str] = Field(None, description="Date of the news")

class ExecutiveSummary(BaseModel):
    headline: str = Field(description="Catchy business intelligence headline")
    summary: str = Field(description="One-page executive brief summarizing findings, challenges, and recommendations")
    pitch: str = Field(description="Personalized, professional consulting pitch addressed to the CEO")

class CompanyOverview(BaseModel):
    name: str = Field(description="Company official name")
    industry: str = Field(description="Primary industry vertical")
    headquarters: str = Field(description="Headquarters city and country")
    geographic_presence: str = Field(description="Countries or regions where the company operates")
    products_services: List[str] = Field(description="Main products and services offered")
    revenue: str = Field(description="Recent annual revenue (e.g. '$15.2B' or 'N/A for Private')")
    funding: str = Field(description="Total funding raised (if private/start-up) or 'Publicly Traded'")
    key_executives: List[str] = Field(description="List of key leadership names and roles")
    expansion_plans: List[str] = Field(description="Recent expansion activities or strategic targets")
    business_challenges: List[str] = Field(description="Key business or operational challenges faced")
    risks: List[str] = Field(description="Strategic, market, or operational risks")

class BIReport(BaseModel):
    company_name: str
    overview: CompanyOverview
    news: List[NewsItem]
    swot: SWOTAnalysis
    competitors: List[CompetitorRow]
    ai_recommendations: List[AIRecommendation]
    executive_summary: ExecutiveSummary
    generated_at: str
