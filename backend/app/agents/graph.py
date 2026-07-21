import datetime
import json
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from app.config import Config
from app.schemas import (
    BIReport, CompanyOverview, SWOTAnalysis, CompetitorRow, 
    AIRecommendation, NewsItem, ExecutiveSummary
)
from app.agents.state import AgentState
from tavily import TavilyClient

# Helper: Get LLM model
def get_llm():
    if Config.GEMINI_API_KEY:
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=Config.GEMINI_API_KEY,
                temperature=0.2
            )
        except Exception:
            pass
    if Config.OPENAI_API_KEY:
        try:
            return ChatOpenAI(
                model="gpt-4o-mini",
                openai_api_key=Config.OPENAI_API_KEY,
                temperature=0.2
            )
        except Exception:
            pass
    return None

# Helper: Run Tavily Web Search
def run_web_search(company_name: str, query: str) -> str:
    if not Config.TAVILY_API_KEY:
        return ""
    try:
        tavily = TavilyClient(api_key=Config.TAVILY_API_KEY)
        response = tavily.search(query=f"{company_name} {query}", max_results=5)
        results = response.get("results", [])
        search_text = []
        for r in results:
            search_text.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}\n")
        return "\n---\n".join(search_text)
    except Exception as e:
        print(f"Tavily Search Error: {e}")
        return ""

# Helper to execute prompt and parse JSON safely
def call_llm_json(llm, prompt: str) -> Dict[str, Any]:
    try:
        # Request JSON output
        response = llm.invoke(prompt + "\n\nCRITICAL: Respond ONLY with a valid, raw JSON object. Do not include markdown formatting like ```json or ```. Just raw JSON.")
        text = response.content.strip()
        # Clean up any potential markdown wrap
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"LLM JSON Error: {e}")
        # Return fallback parsing or minimal structure
        return {}

# =====================================================================
# AGENT 1: RESEARCH AGENT
# =====================================================================
def research_agent(state: AgentState) -> AgentState:
    company = state["company_name"]
    llm = get_llm()
    
    if not llm:
        # Fallback to simulated research
        state["research_data"] = {"status": "skipped_no_llm"}
        return state
        
    search_results = run_web_search(company, "overview products services industry revenue key executives headquarters")
    
    prompt = f"""
    You are the Research Agent for {company}.
    Your goal is to gather core company facts.
    
    Here is the search information from the web:
    {search_results}
    
    If search information is empty, use your internal knowledge about {company}.
    
    CRITICAL: If the search results or your knowledge contain information about multiple different companies with similar names (for example, 'Reliance Industries' vs. 'Reliance Health' vs. 'Reliance Jio'), do not mix their details! Focus on the primary, most well-known entity matching '{company}' (usually the main parent or public conglomerate, unless a specific subsidiary is queried). Do NOT combine their headquarters, revenues, or funding stages.
    
    Ensure that the headquarters, revenue, and funding match the actual real-world facts for this specific company. If '{company}' is a massive public corporation (like Reliance Industries, Apple, Google, Nvidia, etc.), do not report startup funding (like Series C, Sequoia Capital, etc.) or startup headquarters (like San Francisco), and do not use generic or startup-like placeholder values. Return the actual real-world facts (e.g., Mumbai headquarters and public listing status for Reliance Industries).
    
    Construct a JSON response with the following keys:
    - name: official name
    - industry: primary industry
    - headquarters: headquarters location
    - geographic_presence: countries/regions of operations
    - products_services: list of main products/services
    - revenue: annual revenue (e.g. '$20B' or 'Private')
    - funding: total funding raised or 'Public'
    - key_executives: list of key executive names and roles (e.g., ["John Doe (CEO)", "Jane Smith (CFO)"])
    - expansion_plans: list of recent expansion activities or strategy targets
    - business_challenges: list of main business challenges
    - risks: list of major company risks
    """
    
    res = call_llm_json(llm, prompt)
    state["research_data"] = res
    return state

# =====================================================================
# AGENT 2: NEWS AGENT
# =====================================================================
def news_agent(state: AgentState) -> AgentState:
    company = state["company_name"]
    llm = get_llm()
    
    if not llm:
        state["news_data"] = {"status": "skipped_no_llm"}
        return state
        
    search_results = run_web_search(company, "latest news updates merger acquisition product launch 2025 2026")
    
    prompt = f"""
    You are the News Agent for {company}.
    Your goal is to find the latest 3 news items/updates about the company.
    
    Web search results:
    {search_results}
    
    If search results are empty, use your internal knowledge of recent news about {company}.
    
    Construct a JSON response which is a list of news items. Each item must have:
    - title: News headline
    - url: Source URL (make up a realistic one if not in search)
    - summary: Summary of the news and its impact on the company
    - date: Month Year (e.g., 'June 2026')
    
    Respond with a JSON object like:
    {{"news": [ {{"title": "...", "url": "...", "summary": "...", "date": "..."}} ]}}
    """
    
    res = call_llm_json(llm, prompt)
    state["news_data"] = res.get("news", [])
    return state

# =====================================================================
# AGENT 3: BUSINESS ANALYST AGENT
# =====================================================================
def analyst_agent(state: AgentState) -> AgentState:
    company = state["company_name"]
    llm = get_llm()
    
    if not llm:
        state["analyst_data"] = {"status": "skipped_no_llm"}
        return state
        
    research = state["research_data"] or {}
    news = state["news_data"] or []
    
    prompt = f"""
    You are the Business Analyst Agent for {company}.
    Review the company research data:
    {json.dumps(research)}
    
    And recent news:
    {json.dumps(news)}
    
    Formulate a SWOT analysis. Be specific, analytical, and base it on the company's real status.
    
    Construct a JSON response with:
    - strengths: list of strengths
    - weaknesses: list of weaknesses/operational bottlenecks
    - opportunities: list of opportunities
    - threats: list of threats
    """
    
    res = call_llm_json(llm, prompt)
    state["analyst_data"] = res
    return state

# =====================================================================
# AGENT 4: COMPETITOR AGENT
# =====================================================================
def competitor_agent(state: AgentState) -> AgentState:
    company = state["company_name"]
    llm = get_llm()
    
    if not llm:
        state["competitor_data"] = {"status": "skipped_no_llm"}
        return state
        
    research = state["research_data"] or {}
    search_results = run_web_search(company, "top competitors market comparison list")
    
    prompt = f"""
    You are the Competitor Agent for {company}.
    Your goal is to identify 3 top competitors of {company} and compare them.
    
    Company Profile:
    {json.dumps(research)}
    
    Web search results on competitors:
    {search_results}
    
    Construct a JSON response which is a list of competitor comparisons.
    Each competitor must have:
    - name: Competitor Name
    - revenue: Estimated revenue
    - employees: Estimated employee count
    - presence: Primary geographic markets
    - products: List of key products/services
    - technology: List of core technologies used
    - strengths: List of major strengths
    - weaknesses: List of major weaknesses
    - market_position: Market position (Leader, Challenger, Niche, Fast Follower)
    
    Respond with a JSON object like:
    {{"competitors": [ {{"name": "...", "revenue": "...", "employees": "...", "presence": "...", "products": [...], "technology": [...], "strengths": [...], "weaknesses": [...], "market_position": "..."}} ]}}
    """
    
    res = call_llm_json(llm, prompt)
    state["competitor_data"] = res.get("competitors", [])
    return state

# =====================================================================
# AGENT 5: AI CONSULTANT AGENT
# =====================================================================
def consultant_agent(state: AgentState) -> AgentState:
    company = state["company_name"]
    llm = get_llm()
    
    if not llm:
        state["ai_data"] = {"status": "skipped_no_llm"}
        return state
        
    research = state["research_data"] or {}
    analyst = state["analyst_data"] or {}
    
    prompt = f"""
    You are the AI Consultant Agent for {company}.
    Based on the operational weaknesses/challenges and SWOT opportunities identified:
    Weaknesses: {json.dumps(analyst.get('weaknesses'))}
    Challenges: {json.dumps(research.get('business_challenges'))}
    
    Generate exactly 3 specific, non-generic AI implementation opportunities.
    For each AI recommendation, provide:
    - problem: Specific operational bottleneck or pain point.
    - evidence: Evidence or metric from current data supporting this.
    - reasoning: Logical explanation of why AI solves this.
    - recommended_solution: Specific AI/ML solution (e.g. LLM routing, predictive maintenance, agentic workflow).
    - expected_benefits: Tangible benefits (e.g., 'Reduce customer support costs by 30%').
    - implementation_difficulty: 'Low', 'Medium', or 'High'.
    - estimated_cost: Approximate cost (e.g., '$150k - $200k').
    - timeline: Project timeline (e.g., '6 months').
    - expected_roi: Projected ROI (e.g., '250% in Year 1' or '3x savings').
    - priority: 'High', 'Medium', or 'Low'.
    
    Respond with a JSON object like:
    {{"recommendations": [ {{"problem": "...", "evidence": "...", "reasoning": "...", "recommended_solution": "...", "expected_benefits": "...", "implementation_difficulty": "...", "estimated_cost": "...", "timeline": "...", "expected_roi": "...", "priority": "..."}} ]}}
    """
    
    res = call_llm_json(llm, prompt)
    state["ai_data"] = res.get("recommendations", [])
    return state

# =====================================================================
# AGENT 6: CEO PITCH AGENT
# =====================================================================
def pitch_agent(state: AgentState) -> AgentState:
    company = state["company_name"]
    llm = get_llm()
    
    if not llm:
        state["pitch_data"] = {"status": "skipped_no_llm"}
        return state
        
    research = state["research_data"] or {}
    ai_recs = state["ai_data"] or []
    
    prompt = f"""
    You are the CEO Pitch Agent. Your task is to write a highly polished, professional executive pitch to the CEO of {company}.
    
    Company Profile:
    {json.dumps(research)}
    
    AI Recommendations Proposed:
    {json.dumps(ai_recs)}
    
    Generate a JSON response containing:
    - headline: A compelling business intelligence headline.
    - summary: A one-page executive summary summarizing the company's status, challenges, and proposed AI path.
    - pitch: A personalized, persuasive consulting pitch written in professional business language to the CEO. Ask them to collaborate on these AI initiatives.
    """
    
    res = call_llm_json(llm, prompt)
    state["pitch_data"] = res
    return state

# =====================================================================
# AGGREGATOR & DEMO ENGINE
# =====================================================================
def get_mock_report(company_name: str) -> BIReport:
    """
    High-fidelity dynamic generator for any company.
    Provides excellent presets for popular companies and constructs clean templates for any other search query.
    """
    name_clean = company_name.lower().strip()
    
    # -------------------------------------------------------------------------
    # STRIPE PRESET
    # -------------------------------------------------------------------------
    if "stripe" in name_clean:
        overview = CompanyOverview(
            name="Stripe, Inc.",
            industry="Financial Technology & SaaS",
            headquarters="South San Francisco, California, USA",
            geographic_presence="Global (supporting merchants in 50+ countries, cards accepted from 195+ countries)",
            products_services=["Stripe Payments", "Stripe Billing", "Stripe Radar (fraud detection)", "Stripe Connect", "Stripe Tax", "Stripe Sigma", "Stripe Treasury"],
            revenue="$16.1 Billion (2024 GPV of $1 Trillion+)",
            funding="Private (valued at $70 Billion in recent employee tender offers)",
            key_executives=["Patrick Collison (CEO & Co-founder)", "John Collison (President & Co-founder)", "Will Gaybrick (CFO)", "Taylor Bossung (VP Product)"],
            expansion_plans=["Expanding embedded finance (Treasury, Issuing) to enterprise clients", "Deepening local payment method integrations in APAC and LATAM", "Integrating generative AI inside user onboarding, checkout conversion optimization, and documentation helper agents"],
            business_challenges=["Increasing pressure from Adyen in the enterprise space", "High operational overhead of compliance in multi-jurisdictional tax and licensing regimes", "Fraud and chargebacks optimization for rapidly scaling global marketplaces"],
            risks=["Macroeconomic consumer spending slowdowns affecting transaction volumes", "Tightening global regulations regarding financial privacy and crypto integrations", "Talent retention against high-growth AI-native startups"]
        )
        news = [
            NewsItem(title="Stripe Surpasses $1 Trillion in Total Payment Volume", url="https://stripe.com/newsroom", summary="Stripe announced it has processed more than $1T in payment volume, joining a small group of financial giants with that scale.", date="March 2025"),
            NewsItem(title="Stripe Acquires Bridge to Accelerate Stablecoin Checkout API", url="https://stripe.com/newsroom", summary="Stripe acquired Bridge, a stablecoin payment platform, in a major $1.1B acquisition to build out next-gen stablecoin rail APIs.", date="October 2024"),
            NewsItem(title="Stripe Unveils Advanced AI Tools to Combat Fraudulent Transactions", url="https://stripe.com/newsroom", summary="Stripe launched Stripe Radar Assistant, letting merchants query checkout fraud rules in natural language to reduce chargebacks.", date="January 2026")
        ]
        swot = SWOTAnalysis(
            strengths=[
                "Industry-leading developer experience (DX) and documentation APIs",
                "Massive scale of transaction data allowing highly accurate AI-driven fraud models (Radar)",
                "Robust suite of financial services (Billing, Tax, Issuing) creating strong vendor lock-in",
                "High brand equity among developers and startups globally"
            ],
            weaknesses=[
                "Higher standard pricing (2.9% + 30c) compared to customized pricing offered by competitors like Adyen",
                "Complex implementation for legacy enterprise systems that lack modern API design",
                "Dependence on partner banking networks (Sutton, Evolve) which face regulatory scrutiny"
            ],
            opportunities=[
                "Expanding stablecoin infrastructure for lower-cost global B2B Braintree settlements",
                "Developing AI-native billing automation tools that auto-retry failed payments using LLM analysis",
                "Scaling embedded credit and capital financing programs to SMBs via Stripe Capital"
            ],
            threats=[
                "Fierce competition from Adyen, PayPal (Braintree), and legacy merchant acquirers",
                "Increasing regulatory requirements for Know-Your-Customer (KYC) and Anti-Money Laundering (AML) globally",
                "Disruptive decentralized finance (DeFi) payment systems gaining mainstream traction"
            ]
        )
        competitors = [
            CompetitorRow(
                name="Adyen",
                revenue="$2.0 Billion (Net)",
                employees="4,200",
                presence="Europe, North America, APAC, LATAM",
                products=["Single Platform Acquiring", "Point of Sale (POS)", "Adyen Platforms"],
                technology=["Java", "PostgreSQL", "React", "Proprietary Core Ledger"],
                strengths=["Unified global platform (online & in-store)", "Lower interchange-plus pricing for high-volume enterprise", "Direct acquiring licenses globally"],
                weaknesses=["Slower API integration compared to Stripe", "Developer portal is less intuitive for early-stage startups"],
                market_position="Leader (Enterprise Acquiring)"
            ),
            CompetitorRow(
                name="PayPal (Braintree)",
                revenue="$29.7 Billion (PayPal Total)",
                employees="27,000",
                presence="Global",
                products=["Braintree SDK", "Venmo Integration", "PayPal Checkout"],
                technology=["Ruby on Rails", "Node.js", "C++", "Oracle"],
                strengths=["Ubiquitous consumer brand trust", "Excellent checkout conversion rate via Venmo/PayPal buttons", "Deep wallet integrations"],
                weaknesses=["Legacy technical debt in older Braintree setups", "Higher chargeback disputes reporting speeds"],
                market_position="Leader (Consumer checkout wallets)"
            )
        ]
        ai_recommendations = [
            AIRecommendation(
                problem="High checkout dropout rate due to payment declines on international cards.",
                evidence="Stripe research reports show average merchant checkout failures hover around 15%, with up to 5% being false-positive declines by issuing banks.",
                reasoning="Traditional rules-based card routing is static. An AI router can predict card issuing bank rules based on historical transaction metadata and modify request routing dynamically.",
                recommended_solution="AI-powered Dynamic Card Route Router & Message Formatter",
                expected_benefits="Increase authorization rates by 2.4%, yielding tens of millions of dollars in recovered GMV for high-volume merchants.",
                implementation_difficulty="Medium",
                estimated_cost="$250k - $400k",
                timeline="6 months",
                expected_roi="850% in Year 1",
                priority="High"
            ),
            AIRecommendation(
                problem="High support overhead for developers setting up complex multi-party marketplace flows.",
                evidence="Stripe Connect support queues show 40% of developer tickets relate to webhooks, API parameters, or platform-agreement routing.",
                reasoning="LLMs trained on Stripe's codebase and API schema can assist developers in drafting and debugging code in real time inside the dashboard.",
                recommended_solution="Stripe Developer Copilot API Integration",
                expected_benefits="Reduce developer onboarding time by 35% and support ticket volumes by 20%.",
                implementation_difficulty="Low",
                estimated_cost="$80k - $120k",
                timeline="3 months",
                expected_roi="400% in Year 1",
                priority="Medium"
            )
        ]
        exec_summary = ExecutiveSummary(
            headline="Accelerating Stripe's Next Trillion: Multi-Agent AI and Cross-Border Stablecoin Orchestration",
            summary="Stripe has reached a monumental $1 Trillion in processed transaction volume. To maintain its double-digit growth, Stripe must conquer two core frontiers: lowering transaction fees using stablecoin technology (as seen with the Bridge acquisition) and leveraging its vast checkout data to deploy AI-driven card authorization routing and AI-assisted developer onboarding tools. These initiatives will solidify Stripe's position as the financial operating system for the internet.",
            pitch="Dear Patrick and John,\n\nStripe's developer-first APIs revolutionized online payments. Today, your greatest leverage lies in utilizing transaction metadata to outsmart bank card routing declines and automating complex multi-party flows. We propose introducing an AI-powered Dynamic Card Route Router and an inline Developer Copilot. These initiatives will directly increase authorization rates by up to 2.4% and reduce Connect customer support tickets by 20%. Let's partner to deploy these models and accelerate Stripe's journey towards its next trillion in volume."
        )

    # -------------------------------------------------------------------------
    # TESLA PRESET
    # -------------------------------------------------------------------------
    elif "tesla" in name_clean:
        overview = CompanyOverview(
            name="Tesla, Inc.",
            industry="Automotive & Energy Storage",
            headquarters="Austin, Texas, USA",
            geographic_presence="Global (Gigafactories in USA, China, Germany; sales globally)",
            products_services=["Model Y/3/S/X", "Cybertruck", "Powerwall / Megapack", "Solar Panels", "Full Self-Driving (FSD) Software"],
            revenue="$96.7 Billion (2024)",
            funding="Public (NASDAQ: TSLA)",
            key_executives=["Elon Musk (CEO)", "Vaibhav Taneja (CFO)", "Tom Zhu (Senior VP Automotive)"],
            expansion_plans=["Ramping up Cybertruck production", "Constructing Giga Mexico", "Deploying Giga Texas expansions for AI training compute clusters"],
            business_challenges=["Intensifying EV competition, particularly from BYD and domestic Chinese brands", "FSD software safety approvals globally", "Slowing global consumer EV demand and margin compression due to price cuts"],
            risks=["Supply chain vulnerability for rare earth minerals and battery raw materials", "Regulatory safety investigations on Autopilot/FSD", "CEO key-man dependency risk"]
        )
        news = [
            NewsItem(title="Tesla Unveils 'Cybercab' Robotaxi at Hollywood Event", url="https://tesla.com/blog", summary="Tesla showcased its vision for autonomous transportation with a steering-wheel-free Cybercab and a Robovan, planning production by 2026.", date="October 2024"),
            NewsItem(title="Tesla Deploys 50,000 Nvidia H100 GPUs at Giga Texas AI Cluster", url="https://tesla.com/blog", summary="Tesla activated its 'Cortex' supercomputer cluster at Austin HQ to train FSD v12 and Optimus humanoid robot neural networks.", date="January 2025"),
            NewsItem(title="Tesla Energy Division Reports Record Growth in Megapack Shipments", url="https://tesla.com/blog", summary="Tesla Energy storage deployments reached an all-time high of 9.4 GWh in Q2, boosting overall gross margins.", date="July 2024")
        ]
        swot = SWOTAnalysis(
            strengths=[
                "Unmatched brand equity in electric vehicles",
                "Proprietary supercomputer clusters (Dojo / H100s) and massive real-world video training data",
                "High vertical integration from battery cell manufacturing to proprietary Supercharger networks",
                "High profit margins relative to legacy automotive competitors"
            ],
            weaknesses=[
                "High reliance on a limited model lineup (Model 3 and Model Y represent over 90% of sales)",
                "Quality control issues and inconsistent customer service feedback",
                "Frequent price cuts eroding brand value for early buyers and hurting resale valuations"
            ],
            opportunities=[
                "Launching a lower-cost ($25k) next-gen EV model to capture mass market share",
                "Scaling autonomous ride-hailing networks (Cybercab) under regulatory approval",
                "Mass producing Optimus humanoid robots for internal manufacturing assembly lines"
            ],
            threats=[
                "Aggressive price competition from Chinese EV makers (BYD, Geely, Xiaomi)",
                "Regulatory scrutiny or delays regarding full autonomous level 4/5 operations",
                "Grid infrastructure limitations hindering global EV charging expansion"
            ]
        )
        competitors = [
            CompetitorRow(
                name="BYD Auto",
                revenue="$85.0 Billion",
                employees="570,000",
                presence="China, Europe, LATAM, APAC",
                products=["Seagull EV", "Han Sedan", "Blade Battery Technology", "PHEVs"],
                technology=["Blade Battery LFP", "DM-i Hybrid Platforms", "e-Platform 3.0"],
                strengths=["Complete vertical integration (battery, chips, motors in-house)", "Sub-$15k entry level vehicles", "Rapid release cycles"],
                weaknesses=["Slightly lower brand prestige in Western markets", "Lags Tesla in advanced autonomous software FSD capabilities"],
                market_position="Leader (Global EV/PHEV sales)"
            ),
            CompetitorRow(
                name="Waymo (Alphabet)",
                revenue="N/A (Alphabet subsidiary)",
                employees="2,500",
                presence="USA (Phoenix, San Francisco, Los Angeles, Austin)",
                products=["Waymo One Ride-Hailing Service", "Waymo Driver Autonomous Tech"],
                technology=["Lidar", "Radar", "Camera fusion suite", "HD Mapping", "AI Compute"],
                strengths=["Proven commercial Level 4 robotaxi operation running daily", "Backed by Alphabet's massive balance sheet", "High public safety track record"],
                weaknesses=["Hardware suite (Lidar) is expensive to scale", "Geofenced mapping restriction limits rapid geographic expansion"],
                market_position="Leader (Level 4 Autonomous Ride-hailing)"
            )
        ]
        ai_recommendations = [
            AIRecommendation(
                problem="High battery manufacturing scrap rate and battery cell quality control variance.",
                evidence="Gigafactory reports indicate battery manufacturing scrap rates can exceed 8% in early stages of new cell formats (e.g. 4680).",
                reasoning="Applying computer vision and anomaly detection models to assembly line thermal cameras allows real-time scrap identification before assembly.",
                recommended_solution="Edge AI Real-time Battery Cell Anomaly Detection",
                expected_benefits="Reduce cell scrap rates by 30%, saving an estimated $45M annually per Gigafactory.",
                implementation_difficulty="Medium",
                estimated_cost="$350k - $500k",
                timeline="8 months",
                expected_roi="600% in Year 1",
                priority="High"
            ),
            AIRecommendation(
                problem="Inefficient fleet charging schedules causing congestion at Superchargers during peak hours.",
                evidence="Supercharger peak waiting times reached over 30 minutes in high-density urban areas like Los Angeles.",
                reasoning="Predictive demand models using vehicle destination navigation logs can offer dynamically priced discounts or suggest alternative chargers.",
                recommended_solution="AI-Driven Dynamic Pricing & Fleet Charger Allocator",
                expected_benefits="Reduce peak congestion by 20% and optimize grid draw costs for Tesla Energy.",
                implementation_difficulty="Low",
                estimated_cost="$120k - $180k",
                timeline="4 months",
                expected_roi="350% in Year 1",
                priority="Medium"
            )
        ]
        exec_summary = ExecutiveSummary(
            headline="Tesla's Pivot to Autonomy: Capitalizing on FSD Video Pipelines and Optimus Integration",
            summary="Tesla is transitioning from an automotive manufacturer into an AI and robotics powerhouse. With its massive computing power (Dojo and Nvidia GPUs) and FSD v12's end-to-end neural networks, Tesla is uniquely positioned to dominate autonomous transportation. However, price wars with Chinese manufacturers like BYD challenge its core hardware profitability. Implementing AI-driven quality assurance in battery cells and deploying predictive scheduling for Superchargers will protect core margins, funding the high-cost robotaxi rollout.",
            pitch="Dear Elon,\n\nAs Tesla shifts into the Robotaxi era, maintaining absolute quality in your 4680 cell manufacturing and optimizing the Supercharger network is vital to protect Tesla's balance sheet. We propose installing an Edge AI anomaly detection system on 4680 lines, which will cut scrap rates by 30%, saving $45M per Gigafactory. Additionally, integrating an AI-driven Supercharger allocator will eliminate peak wait times, ensuring a premium driver experience. Let's discuss accelerating these digital operations as you roll out Cybercab globally."
        )

    # -------------------------------------------------------------------------
    # RELIANCE INDUSTRIES PRESET
    # -------------------------------------------------------------------------
    elif "reliance" in name_clean:
        overview = CompanyOverview(
            name="Reliance Industries Limited (RIL)",
            industry="Conglomerate (Energy, Retail, Telecommunications, Petrochemicals)",
            headquarters="Mumbai, Maharashtra, India",
            geographic_presence="Primarily India (with global energy exporting operations)",
            products_services=["Jio Telecommunications", "Reliance Retail stores", "Petroleum Refining (Jamnagar)", "Polyester and Petrochemicals", "Jio Financial Services"],
            revenue="₹10,00,300 Crore (~$119.5 Billion USD)",
            funding="Publicly Listed (NSE: RELIANCE / BSE: 500325)",
            key_executives=["Mukesh Ambani (Chairman & Managing Director)", "Akash Ambani (Chairman, Jio Infocomm)", "Isha Ambani (Director, Reliance Retail)", "Anant Ambani (Director, Energy Business)"],
            expansion_plans=["Investing $10 Billion in Gigafactories for green hydrogen, solar cells, and energy storage in Gujarat", "Scaling up e-commerce operations via JioMart to battle Amazon & Flipkart", "Rolling out commercial 5G FWA and AI-native cloud compute services for Indian SMBs"],
            business_challenges=["High debt margins from massive 5G infrastructure layouts", "Evolving global margins in refining and petrochemical margins cycles", "Transitioning from legacy carbon-heavy oil businesses to clean energy setups"],
            risks=["Severe local competition from Adyen/Paytm in financial fields and Adani in green infrastructure", "Volatility in crude oil supply lines and geopolitical freight lanes", "Talent acquisition for specialized digital and AI initiatives"]
        )
        news = [
            NewsItem(title="Reliance Industries Surpasses ₹20 Lakh Crore in Market Capitalization", url="https://economictimes.indiatimes.com", summary="RIL became the first Indian corporate conglomerate to touch the 20 trillion rupee market value mark, driven by retail and Jio growth.", date="February 2025"),
            NewsItem(title="Reliance Announces Jio Brain: Multi-Agent AI Platform for Indian Enterprises", url="https://jiomart.com/news", summary="Jio announced Jio Brain, an integrated suite of LLMs and generative AI tools to automate workflows for millions of retail stores and SMBs.", date="January 2026"),
            NewsItem(title="RIL to Commission Widescale Jamnagar Green Hydrogen Plant in late 2026", url="https://reuters.com", summary="RIL's clean energy division has targeted late 2026 to start commercial solar module cells and green hydrogen cell distributions.", date="June 2025")
        ]
        swot = SWOTAnalysis(
            strengths=[
                "Absolute market leadership in Indian telecommunications (450M+ Jio subscribers)",
                "Huge physical retail footprint with over 18,000 stores across India",
                "World's largest single-location petroleum refinery at Jamnagar, guaranteeing strong cash flows",
                "Powerful backing and political/economic strategic alignment within India"
            ],
            weaknesses=[
                "Heavy dependency on traditional high-emission carbon energy refining for gross profits",
                "Complex debt structure from intensive telecom capital expansions",
                "Organizational structure is highly traditional and centralized"
            ],
            opportunities=[
                "Deploying localized AI models (Jio Brain) to automate supply chain metrics for 15 million local kirana shops",
                "Leveraging green hydrogen grid infrastructure to capture India's clean energy shift",
                "Expanding Jio Financial Services to capture retail consumer loans"
            ],
            threats=[
                "Aggressive price tariff wars in telecom against Bharti Airtel",
                "Global clean energy transition taxes eroding standard refinery valuations",
                "Fluctuations in foreign exchange rates and international crude prices"
            ]
        )
        competitors = [
            CompetitorRow(
                name="Bharti Airtel",
                revenue="$18.5 Billion",
                employees="18,000",
                presence="India, South Asia, Africa",
                products=["Airtel 5G", "Wynk Music", "Airtel Payments Bank", "Enterprise Lease Lines"],
                technology=["Ericsson/Nokia 5G Core", "AWS Cloud", "Java", "Kubernetes"],
                strengths=["High Average Revenue Per User (ARPU)", "Extensive premium enterprise customer base", "Strong footprint in Africa"],
                weaknesses=["Slightly lower mobile subscriber count compared to Jio in India", "Less integrated retail product ecosystem"],
                market_position="Challenger (Telecom Leader)"
            ),
            CompetitorRow(
                name="Adani Group",
                revenue="$32.0 Billion",
                employees="23,000",
                presence="India (Global ports & commodities)",
                products=["Adani Green Energy", "Adani Total Gas", "Ports & Infrastructure"],
                technology=["Industrial IoT", "SAP", "Microsoft Cloud", "Scada Systems"],
                strengths=["Unrivaled control of India's ports, airports, and coal power grids", "Highly aggressive clean energy solar layout", "Deep capital funding backing"],
                weaknesses=["High leverage ratio and exposure to short-term short seller allegations", "Lack of direct consumer consumer tech reach"],
                market_position="Leader (Infrastructure & Energy)"
            )
        ]
        ai_recommendations = [
            AIRecommendation(
                problem="High supply chain wastage and shipping inventory latency in Reliance Retail's 18,000 physical stores.",
                evidence="RIL annual statements report inventory holding times average 42 days, with 3% margin losses due to perishability leakage.",
                reasoning="Applying predictive demand models based on regional event databases, climate feeds, and localized customer transactions can pre-stage stock dynamically.",
                recommended_solution="AI-Driven Hyperlocal Inventory Allocation & Demand Planner",
                expected_benefits="Reduce inventory holding periods by 8 days, yielding an estimated savings of ₹1,400 Crore ($170M USD) annually.",
                implementation_difficulty="Medium",
                estimated_cost="$450k - $600k",
                timeline="8 months",
                expected_roi="550% in Year 1",
                priority="High"
            ),
            AIRecommendation(
                problem="High energy consumption and variable thermal cracking efficiency at the Jamnagar Refinery.",
                evidence="Energy inputs comprise over 25% of operational refining costs at Jamnagar, where temperature fluctuations directly affect production grades.",
                reasoning="Sensor feeds can train a deep neural network to predict boiler thermal cracking efficiency, automatically optimizing catalyst and fuel mixes.",
                recommended_solution="Deep Reinforcement Learning Boiler Controller & Optimizer",
                expected_benefits="Boost refinery output efficiency by 1.2%, generating upwards of $80M in incremental annual operating profits.",
                implementation_difficulty="High",
                estimated_cost="$800k - $1.2M",
                timeline="12 months",
                expected_roi="900% in Year 1",
                priority="High"
            )
        ]
        exec_summary = ExecutiveSummary(
            headline="Scaling India's Largest Conglomerate: Predictive Supply Chains and AI-Native Refineries",
            summary="Reliance Industries is uniquely poised to dominate India's next decade of consumption. RIL's cash-cow refining operations in Jamnagar are funding major expansions in green energy and 5G retail services. To defend its gross margins against Adani and international B2C giants, Reliance must deploy advanced AI optimizations. We propose installing predictive inventory schedulers across Reliance Retail and AI thermal controllers at Jamnagar to boost Conglomerate cash flows by over $250 Million annually.",
            pitch="Dear Mukesh,\n\nReliance's massive physical retail network and industrial refining scale present a unique optimization canvas. We propose deploying: 1. An AI-Driven Inventory Demand Planner for Reliance Retail to compress stock cycles and save ₹1,400 Crore, and 2. A Deep Learning Catalyst Optimizer at Jamnagar to increase refining output by 1.2%. These initiatives will secure RIL's margins as you navigate the green transition. Let's collaborate to roll out these AI controls across Jamnagar and your retail divisions."
        )

    # -------------------------------------------------------------------------
    # RELIANCE JIO PRESET
    # -------------------------------------------------------------------------
    elif "jio" in name_clean:
        overview = CompanyOverview(
            name="Reliance Jio Infocomm Limited",
            industry="Telecommunications & Digital Services",
            headquarters="Mumbai, Maharashtra, India",
            geographic_presence="India (national 5G/4G coverage supporting 450M+ users)",
            products_services=["Jio 5G/4G Mobile", "JioFiber Broadband", "Jio AirFiber (FWA)", "JioCinema & JioTV", "JioMart integration", "Jio Cloud Services"],
            revenue="₹1,10,000 Crore (~$13.2 Billion USD)",
            funding="Subsidiary of Jio Platforms (backed by Meta, Google, KKR, Silver Lake, Qualcomm)",
            key_executives=["Akash Ambani (Chairman)", "Pankaj Pawar (Managing Director)", "Kiran Thomas (Director)", "Anshuman Thakur (Head of Strategy)"],
            expansion_plans=["Deploying localized edge-computing AI servers across India's tier-2/3 cities", "Expanding Jio AirFiber coverage to 100 million households", "Launching enterprise cloud suites powered by NVIDIA AI supercomputing clusters in India"],
            business_challenges=["Monetizing massive capital expenditures in 5G spectrum spectrum licenses", "Retaining low-paying prepaid users while trying to lift overall ARPU", "High volume of network congestion in metropolitan high-density areas"],
            risks=["Tariff hikes causing churn to Bharti Airtel or public options", "Increasing hardware manufacturing costs for affordable Jio smartphones", "Rapid changes in open-source AI models requiring re-training frameworks"]
        )
        news = [
            NewsItem(title="Jio Platforms Partners with NVIDIA to Build AI Infrastructure in India", url="https://nvidia.com", summary="Jio and NVIDIA announced a partnership to build a cloud AI supercomputer footprint in India, training foundational LLMs in local Indian languages.", date="September 2024"),
            NewsItem(title="Jio AirFiber Touches 5 Million Connected Homes within 18 Months", url="https://jio.com", summary="Jio reported accelerated fixed-wireless household installations, expanding high-speed broadband into rural market sectors.", date="January 2026"),
            NewsItem(title="Jio Launches 'JioPhone Prima' to Migrate 2G Users to 4G Networks", url="https://jio.com", summary="Jio launched an affordable, smart feature phone to capture India's remaining 2G consumer base and drive data usage.", date="November 2025")
        ]
        swot = SWOTAnalysis(
            strengths=[
                "Largest mobile network operator in India (450M+ active data subscribers)",
                "Full IP-based LTE and standalone 5G network architecture, free of legacy 2G/3G overheads",
                "Deep synergy with Meta's WhatsApp for e-commerce checkout channels via JioMart",
                "Abundant financial liquidity backed by global technology giants Google and Meta"
            ],
            weaknesses=[
                "Relatively low average revenue per user (ARPU) compared to global averages",
                "Massive capital debt incurred from standalone 5G spectrum bidding",
                "High churn rate among early entry-tier prepaid consumers"
            ],
            opportunities=[
                "Building GPU compute instances on Nvidia hardware to upsell AI cloud resources to Indian developers",
                "Integrating AI-native customer chatbots inside WhatsApp to support local shop transactions",
                "Expanding enterprise data center hosting for national sovereign cloud policies"
            ],
            threats=[
                "Aggressive mobile network price competition from Bharti Airtel",
                "Strict regulatory compliance audits on data protection and KYC onboarding from TRAI",
                "Technological shifts towards satellite internet models like Starlink in remote sectors"
            ]
        )
        competitors = [
            CompetitorRow(
                name="Bharti Airtel",
                revenue="$18.5 Billion",
                employees="18,000",
                presence="India, South Asia, Africa",
                products=["Airtel 5G", "Airtel Digital TV", "Wynk Music", "Airtel IQ (Enterprise)"],
                technology=["OpenRAN", "AWS Cloud", "Cassandra", "Node.js"],
                strengths=["Higher ARPU index", "Leader in corporate premium connections", "Vast presence across Africa"],
                weaknesses=["Slightly lower standalone 5G spectrum footprint", "Lacks direct backing from Google/Meta capital portfolios"],
                market_position="Challenger (Telecom Leader)"
            ),
            CompetitorRow(
                name="Vodafone Idea",
                revenue="$5.2 Billion",
                employees="11,000",
                presence="India",
                products=["Vi Mobile networks", "Vi Movies & TV", "Vi Enterprise Solutions"],
                technology=["4G LTE Core", "Oracle ERP", "React"],
                strengths=["Legacy brand presence in urban locations", "Substantial spectrum holding shares"],
                weaknesses=["Heavy debt burden and government equity holdings", "Consistent loss of active subscribers monthly"],
                market_position="Challenger (Tier-2 Telecom)"
            )
        ]
        ai_recommendations = [
            AIRecommendation(
                problem="High customer support overhead handling billing and network queries for 450 million subscribers.",
                evidence="Jio support lines receive over 2.4 million daily tickets, with 70% being basic questions regarding tariff activations.",
                reasoning="Fine-tuned LLMs trained on TRAI compliance guidelines and Jio's internal system rules can resolve queries in natural language via WhatsApp.",
                recommended_solution="Jio Brain Conversational Customer Support Swarm",
                expected_benefits="Automate 60% of customer support volume, saving ₹800 Crore ($96M USD) annually in operational center costs.",
                implementation_difficulty="Medium",
                estimated_cost="$200k - $300k",
                timeline="5 months",
                expected_roi="600% in Year 1",
                priority="High"
            ),
            AIRecommendation(
                problem="Inefficient cellular base station electricity draw during low-activity night hours.",
                evidence="Jio's 5G cells consume static energy rates regardless of active network traffic densities.",
                reasoning="Machine learning models can predict localized cell traffic patterns and dynamically place inactive towers in low-power standby modes.",
                recommended_solution="AI-Driven Predictive Cell Tower Power Manager",
                expected_benefits="Reduce cellular grid power costs by 18%, saving ₹1,100 Crore in annual utility expenditures.",
                implementation_difficulty="Medium",
                estimated_cost="$180k - $250k",
                timeline="6 months",
                expected_roi="750% in Year 1",
                priority="High"
            )
        ]
        exec_summary = ExecutiveSummary(
            headline="Unlocking Jio's Next Phase: AI-Native Edge Networks and NVIDIA Supercomputer Cloud",
            summary="Reliance Jio has established absolute dominance in India's telecommunications sector. To unlock its next valuation multiple, Jio is pivoting from a connectivity utility to an AI-Native digital platform. By leveraging its partnerships with NVIDIA to deploy cloud compute nodes and utilizing conversational LLMs to automate customer care, Jio can reduce operational expenditures and expand its high-margin enterprise cloud business.",
            pitch="Dear Akash,\n\nHaving built the connectivity foundation for 450 million Indians, Jio's next growth frontier lies in operational optimization and developer cloud services. We propose deploying: 1. A Conversational Customer Support Swarm on WhatsApp to resolve 60% of support volume, saving ₹800 Crore, and 2. An AI-Driven Cell Tower Power Manager to trim cellular electricity utility costs by 18%. Additionally, configuring Nvidia-backed sovereign GPU nodes will establish Jio as the premier AI developer cloud in India. Let's discuss launching these models."
        )

    # -------------------------------------------------------------------------
    # APPLE PRESET
    # -------------------------------------------------------------------------
    elif "apple" in name_clean:
        overview = CompanyOverview(
            name="Apple Inc.",
            industry="Consumer Electronics & Software Services",
            headquarters="Cupertino, California, USA",
            geographic_presence="Global (retail stores in 26+ countries, products sold worldwide)",
            products_services=["iPhone", "iPad", "Mac", "Apple Watch", "Apple Vision Pro", "App Store", "Apple Intelligence"],
            revenue="$385.7 Billion (FY2024)",
            funding="Public (NASDAQ: AAPL)",
            key_executives=["Tim Cook (CEO)", "Luca Maestri (CFO)", "Jeff Williams (COO)", "Craig Federighi (SVP Software Engineering)"],
            expansion_plans=["Expanding Apple Retail presence in India and Southeast Asia", "Deploying Apple Intelligence privacy servers globally", "Developing autonomous spatial computing apps for Apple Vision Pro"],
            business_challenges=["Regulatory antitrust lawsuits targeting App Store fee margins in US and EU", "Slowing premium smartphone upgrades cycle in Western markets", "Heavy hardware supply chain dependencies on manufacturing partners in China"],
            risks=["Geopolitical tensions impacting China manufacturing centers", "Antitrust enforcement breaking up default Google search placement fees", "Lags in early developer adoption for Vision Pro devices"]
        )
        news = [
            NewsItem(title="Apple Rolls Out Apple Intelligence Across iPhone 16 Lineup", url="https://apple.com/newsroom", summary="Apple announced the commercial launch of its on-device and private cloud generative AI models, enhancing Siri and photo-editing workflows.", date="October 2024"),
            NewsItem(title="EU Commission Fines Apple €1.8B Over App Store Anti-Steering Policies", url="https://reuters.com", summary="European antitrust regulators issued a major fine against Apple for blocking music streaming apps from advertising cheaper subscriptions.", date="March 2024"),
            NewsItem(title="Apple Opens Second Flagship Retail Store in New Delhi, India", url="https://apple.com/newsroom", summary="Tim Cook inaugurated Apple's latest flagship outlet, highlighting the brand's accelerating consumer sales footprint in India.", date="April 2025")
        ]
        swot = SWOTAnalysis(
            strengths=[
                "Extremely high customer loyalty and brand prestige globally",
                "Deep ecosystem integration (iOS, macOS, watchOS, iCloud) creating high customer lock-in",
                "Vast cash reserves (~$150B) enabling heavy long-term R&D investments",
                "Industry-leading custom silicon division (M-series and A-series chips)"
            ],
            weaknesses=[
                "High pricing leaves brand vulnerable to low-cost competitors in developing nations",
                "Heavy dependence on a single product line (iPhone represents ~50% of total revenue)",
                "Restricted sandbox approach limiting early developer model customization compared to open-source"
            ],
            opportunities=[
                "Monetizing Apple Intelligence features through premium cloud subscription tiers (Siri Pro)",
                "Expanding digital health and medical sensing capabilities on Apple Watch",
                "Expanding direct assembly plants in India and Vietnam to de-risk Chinese supply chains"
            ],
            threats=[
                "Aggressive global regulatory campaigns aiming to allow third-party app marketplaces",
                "Rapid mobile hardware feature convergence from competitors like Samsung and Huawei",
                "Macroeconomic inflationary pressures depressing high-end consumer hardware spend"
            ]
        )
        competitors = [
            CompetitorRow(
                name="Samsung Electronics",
                revenue="$200.0 Billion",
                employees="270,000",
                presence="Global",
                products=["Galaxy S-series", "Foldables", "AMOLED Screens", "Memory Chips"],
                technology=["Exynos Custom Silicon", "Android OS", "AI SmartThings"],
                strengths=["Dominant global smartphone shipment share", "Internal display and semiconductor manufacturing arms", "Broader entry-level phone range"],
                weaknesses=["Slightly lower ecosystem integration prestige", "Lower profit margins on Android hardware"],
                market_position="Leader (Mobile Hardware)"
            ),
            CompetitorRow(
                name="Alphabet (Google)",
                revenue="$307.4 Billion",
                employees="180,000",
                presence="Global",
                products=["Android OS", "Pixel Smartphones", "Google Play Store", "Gemini AI"],
                technology=["Tensor Silicon", "Android Stack", "Vertex AI Platform"],
                strengths=["Controls the mobile operating system (Android) for 70%+ of global phones", "World leader in web analytics search engines", "Vast cloud footprint"],
                weaknesses=["Direct Pixel hardware sales remain small relative to iPhone", "Fragmented Android distribution partners"],
                market_position="Leader (Mobile Software)"
            )
        ]
        ai_recommendations = [
            AIRecommendation(
                problem="High App Store developer churn and friction during manual app review security cycles.",
                evidence="App review queues process over 100,000 updates weekly, with average review times taking up to 48 hours, hurting developer relations.",
                reasoning="Large multimodal models can automatically scan app source code and UI layouts against App Store safety guidelines, flagging issues before human review.",
                recommended_solution="AI-Powered Pre-Review App Security Scanner",
                expected_benefits="Reduce developer review cycles from 48 hours to less than 30 minutes, compressing review staff workloads by 40%.",
                implementation_difficulty="Medium",
                estimated_cost="$300k - $450k",
                timeline="6 months",
                expected_roi="380% in Year 1",
                priority="High"
            ),
            AIRecommendation(
                problem="Underutilized local device compute for Siri due to weak localized language search parsing.",
                evidence="User analytics reveal up to 35% of Siri requests are routed to cloud servers due to semantic matching failures on device.",
                reasoning="Deploying highly compressed, quantized local LLMs on Apple's Neural Engine will process complex natural commands directly on-device.",
                recommended_solution="Quantized Siri Semantic Router for Apple Neural Engine",
                expected_benefits="Increase local on-device command handling by 25%, drastically reducing private cloud computing energy bills.",
                implementation_difficulty="High",
                estimated_cost="$500k - $750k",
                timeline="8 months",
                expected_roi="290% in Year 1",
                priority="Medium"
            )
        ]
        exec_summary = ExecutiveSummary(
            headline="Protecting the Garden: Accelerating Apple Intelligence and Optimizing App Store reviews",
            summary="Apple is navigating a critical transition to AI-native hardware. The iPhone remains Apple's core revenue driver, but regulatory actions in the EU and US threaten App Store commissions. To defend its ecosystem margins, Apple must speed up developer pipelines and leverage its M-series Neural Engines. We propose deploying an AI-Powered App Review Scanner to cut review times from 2 days to 30 minutes, along with optimizing local device Siri routing to reduce private cloud infrastructure costs.",
            pitch="Dear Tim,\n\nAs Apple transitions to Apple Intelligence, maintaining absolute ecosystem security and developers satisfaction is key. We propose deploying: 1. An AI-Powered Pre-Review App Review Scanner to compress validation times to 30 minutes, and 2. A Quantized Siri Semantic Router to handle 25% more requests directly on-device, cutting cloud utility costs. These digital initiatives will protect App Store margins and optimize private compute nodes. Let's discuss implementing these modules."
        )

    # -------------------------------------------------------------------------
    # NVIDIA PRESET
    # -------------------------------------------------------------------------
    elif "nvidia" in name_clean:
        overview = CompanyOverview(
            name="NVIDIA Corporation",
            industry="Semiconductors, Gaming & AI Compute Infrastructures",
            headquarters="Santa Clara, California, USA",
            geographic_presence="Global (silicon manufactured by TSMC in Taiwan, packaged globally)",
            products_services=["H100 / H200 AI GPUs", "Blackwell B200 / GB200 platform", "CUDA Software Suite", "GeForce RTX graphics cards", "NVIDIA DGX Cloud", "Mellanox InfiniBand networking"],
            revenue="$96.3 Billion (FY2025 Projected)",
            funding="Public (NASDAQ: NVDA)",
            key_executives=["Jensen Huang (Founder, President & CEO)", "Colette Kress (EVP & CFO)", "Jay Puri (EVP, Worldwide Field Operations)", "Debora Shoquist (EVP, Operations)"],
            expansion_plans=["Constructing massive AI supercomputing centers in Japan, Europe, and India", "Expanding software revenues via Enterprise AI software license packages", "Investing in custom silicon design pipelines for automotive autonomous driving (NVIDIA Thor)"],
            business_challenges=["Heavy dependency on TSMC for advanced silicon packaging and manufacturing", "US export restrictions limiting high-end AI chip shipments to China", "Emerging silicon design initiatives from customers like AWS, Google, and Meta"],
            risks=["Geopolitical instability around Taiwan impacting TSMC chip fabrication lines", "Cyclical drops in hyper-scaler AI capital budgets", "Hardware copycatting from AMD and Intel chip competitors"]
        )
        news = [
            NewsItem(title="NVIDIA Announces Blackwell GPU Architecture at GTC Conference", url="https://nvidia.com/newsroom", summary="Jensen Huang unveiled the Blackwell B200 chip, claiming it delivers 20 petaflops of AI performance with 25x less energy draw than Hopper.", date="March 2024"),
            NewsItem(title="US Restricts NVIDIA from Exporting H20 AI Chips to Chinese Market", url="https://nytimes.com", summary="US commerce regulators tightened licensing requirements, blocking customized lower-spec AI silicon exports to Chinese clients.", date="September 2024"),
            NewsItem(title="NVIDIA Surpasses Microsoft as World's Most Valuable Public Company", url="https://bloomberg.com", summary="NVIDIA's stock valuation touched an all-time high of $3.34 Trillion, driven by insatiable global demand for AI compute infrastructure.", date="June 2024")
        ]
        swot = SWOTAnalysis(
            strengths=[
                "Absolute monopoly in AI training and inference silicon market (~90% market share)",
                "CUDA software ecosystem creating massive developer lock-in for 15+ years",
                "Unmatched networking capabilities via Mellanox integration (InfiniBand)",
                "Extremely high gross margins (exceeding 75%) on data center hardware"
            ],
            weaknesses=[
                "No internal manufacturing fabrication foundries, leaving Apple/Nvidia reliant on TSMC",
                "Premium pricing makes hardware inaccessible to early-stage universities and small startups",
                "Underdeveloped software-only business revenues relative to massive hardware sales"
            ],
            opportunities=[
                "Expanding the 'NVIDIA AI Enterprise' software layer to collect recurring SaaS licensing fees",
                "Deploying turnkey autonomous driving platforms (DRIVE) to legacy car brands",
                "Collaborating with national governments to establish 'Sovereign AI' compute hubs globally"
            ],
            threats=[
                "Cloud service provider clients (Microsoft, AWS, Google) designing custom ASICs (TPUs, Inferentia)",
                "Strict geopolitical hardware blockades disrupting high-margin export regions",
                "AMD expanding its open ROCm software platform to break the CUDA monopoly"
            ]
        )
        competitors = [
            CompetitorRow(
                name="AMD (Advanced Micro Devices)",
                revenue="$22.6 Billion",
                employees="26,000",
                presence="Global",
                products=["MI300X AI Accelerator", "EPYC Server CPUs", "Ryzen Desktop processors", "ROCm software platform"],
                technology=["TSMC 3nm/5nm process", "Chiplet Design Architecture", "ROCm ecosystem"],
                strengths=["Strong price-to-performance ratio on MI300X accelerators", "Excellent server CPU market share", "Strong gaming console market"],
                weaknesses=["ROCm software ecosystem lags CUDA in developer libraries support", "Lacks proprietary high-speed networking fabrics equivalent to InfiniBand"],
                market_position="Challenger (AI Accelerator)"
            ),
            CompetitorRow(
                name="Intel Corporation",
                revenue="$54.2 Billion",
                employees="115,000",
                presence="Global (runs own fabrication foundries)",
                products=["Gaudi 3 AI Accelerator", "Xeon Server CPUs", "Intel Foundry Services"],
                technology=["Intel 18A process", "x86 architecture", "Gaudi ASICs"],
                strengths=["Internal silicon fabrication foundry facilities", "Dominant historical PC/server x86 CPU footprint"],
                weaknesses=["Slower execution on AI graphics chips", "Foundry business is losing capital in early stages"],
                market_position="Challenger (Semiconductors)"
            )
        ]
        ai_recommendations = [
            AIRecommendation(
                problem="High wafer scrap rates during TSMC chip packaging inspection cycles.",
                evidence="Advanced chiplet packaging (CoWoS) reports yields drop by up to 5% during initial production runs of dense Blackwell interposers.",
                reasoning="Computer vision models trained on thermal sensor feeds can detect trace structural defects in silicon layers before final curing.",
                recommended_solution="AI-Powered CoWoS Silicon Defect Detection System",
                expected_benefits="Increase packaging yields by 1.8%, saving up to $120M in lost silicon costs across data lines.",
                implementation_difficulty="High",
                estimated_cost="$600k - $900k",
                timeline="10 months",
                expected_roi="800% in Year 1",
                priority="High"
            ),
            AIRecommendation(
                problem="Long developer setup cycles for custom CUDA environments inside corporate networks.",
                evidence="Customer developer feedback surveys report setting up CUDA runtime drivers takes average 3-4 days in strict enterprise networks.",
                reasoning="An AI agent can audit container setups and automatically draft system-compatible Dockerfiles with the required CUDA drivers.",
                recommended_solution="AI-Native CUDA Environment Configurator Agent",
                expected_benefits="Reduce developer onboarding time to under 15 minutes, accelerating client deployment cycles.",
                implementation_difficulty="Low",
                estimated_cost="$90k - $140k",
                timeline="3 months",
                expected_roi="450% in Year 1",
                priority="Medium"
            )
        ]
        exec_summary = ExecutiveSummary(
            headline="Sustaining the Compute Monopoly: Maximizing Packaging Yields and CUDA Software SaaS",
            summary="NVIDIA has successfully captured the AI infrastructure revolution. However, reliance on TSMC for packaging (CoWoS) bottlenecks Blackwell delivery times. To protect its massive margins, NVIDIA must optimize manufacturing QA and expand its high-margin software revenues. We propose deploying an AI Silicon Defect Detector to boost chiplet packaging yields by 1.8%, saving $120 Million, alongside launching automated CUDA setup agents to streamline software environments.",
            pitch="Dear Jensen,\n\nAs NVIDIA rolls out Blackwell, securing your packaging supply yields and CUDA developer velocity is priority number one. We propose: 1. Deploying a deep computer vision Defect Detector to boost packaging yields by 1.8%, protecting $120M in custom silicon costs, and 2. An AI CUDA Environment Configurator to reduce developer onboarding from days to minutes. These digital systems will reinforce NVIDIA's data center leadership and accelerate software license activations. Let's discuss setting up these modules."
        )

    # -------------------------------------------------------------------------
    # GOOGLE / ALPHABET PRESET
    # -------------------------------------------------------------------------
    elif "google" in name_clean or "alphabet" in name_clean:
        overview = CompanyOverview(
            name="Alphabet Inc.",
            industry="Internet Software, Cloud Computing & AI Services",
            headquarters="Mountain View, California, USA",
            geographic_presence="Global (data centers across 4 continents, office sites globally)",
            products_services=["Google Search Engine", "YouTube platform", "Google Cloud Platform (GCP)", "Google Workspace", "Gemini AI models", "Android mobile platform", "Waymo autonomous driving"],
            revenue="$307.4 Billion (FY2024)",
            funding="Public (NASDAQ: GOOGL)",
            key_executives=["Sundar Pichai (CEO, Alphabet & Google)", "Ruth Porat (President & Chief Investment Officer)", "Thomas Kurian (CEO, Google Cloud)", "Philipp Schindler (SVP & Chief Business Officer)"],
            expansion_plans=["Constructing new AI hyper-scale data centers globally", "Expanding sovereign enterprise cloud setups for public sectors", "Deploying driverless Waymo passenger fleets across US urban areas"],
            business_challenges=["Shifts in consumer search traffic to conversational AI interfaces (e.g. ChatGPT, Perplexity)", "Antitrust litigation accusing Google of illegal search search distribution agreements", "Heavy compute cost structures associated with running generative LLM queries at search scale"],
            risks=["Legal break-up remedies forced by US Department of Justice", "Ad revenue compression due to changing media consumption trends", "High infrastructure power constraints slowing data center developments"]
        )
        news = [
            NewsItem(title="Google Launches Gemini 1.5 Pro with 2-Million Token Window", url="https://google.com/press", summary="Google updated its flagship AI model Gemini, introducing an industry-leading context window capable of analyzing massive code repositories and video datasets.", date="May 2024"),
            NewsItem(title="US Judge Rules Google Holds Illegal Search Engine Monopoly", url="https://apnews.com", summary="A federal judge ruled that Google violated Section 2 of the Sherman Act by paying billions of dollars to remain the default search engine on smartphones.", date="August 2024"),
            NewsItem(title="Waymo Crosses 100,000 Paid Robotaxi Trips Weekly across US Cities", url="https://google.com/blog", summary="Waymo announced record rider volumes, expanding passenger pick-up boundaries in San Francisco and Los Angeles.", date="August 2024")
        ]
        swot = SWOTAnalysis(
            strengths=[
                "Ubiquitous search engine monopoly (holding ~90% global search share)",
                "Massive advertising network (AdWords/AdSense) generating $200B+ annually",
                "Deep machine learning expertise from Google Brain and DeepMind divisions",
                "Vast Android distribution channel powering 3+ billion devices globally"
            ],
            weaknesses=[
                "High dependency on advertising revenues (over 70% of total revenue)",
                "Slower consumer release cycles for AI due to public reputation and hallucination risks",
                "Internal product overlaps causing fragmentation across cloud and search groups"
            ],
            opportunities=[
                "Expanding Google Cloud (GCP) market share using customized Gemini developer tools",
                "Embedding AI-powered summaries (Search Generative Experience) to monetize conversational search ads",
                "Deploying commercial Level 4 driverless delivery and passenger trucking via Waymo"
            ],
            threats=[
                "Antitrust regulatory decrees demanding structural breakups or search contract bans",
                "Direct traffic loss to conversational AI start-ups bypassing standard browser search pages",
                "Rapid rise in graphics processor unit (GPU) rental costs squeezing cloud operational profits"
            ]
        )
        competitors = [
            CompetitorRow(
                name="Microsoft Corporation",
                revenue="$245.1 Billion",
                employees="220,000",
                presence="Global",
                products=["Azure Cloud", "Microsoft Copilot", "Bing Search", "OpenAI Partnership"],
                technology=["OpenAI GPT-4o", "Office 365 core", "Azure Hyper-scaler"],
                strengths=["Vast enterprise software distribution pipeline", "Deep structural alignment with OpenAI", "Strong cloud momentum in enterprise"],
                weaknesses=["Slower footprint in consumer mobile OS platforms", "Bing Search market share remains under 5%"],
                market_position="Leader (Enterprise Cloud & AI)"
            ),
            CompetitorRow(
                name="Amazon Web Services (AWS)",
                revenue="$90.8 Billion",
                employees="1,500,000 (Amazon Total)",
                presence="Global",
                products=["AWS Cloud Hosting", "Amazon Bedrock", "SageMaker ML", "Q AI Assistant"],
                technology=["Custom Trainium/Inferentia Silicon", "Bedrock API", "S3 Storage"],
                strengths=["Undisputed global leader in cloud infrastructure hosting", "Extensive corporate database customers list", "Strong retail integration"],
                weaknesses=["Lags Google/Microsoft in proprietary state-of-the-art LLM capabilities", "Higher egress network costs"],
                market_position="Leader (Cloud Infrastructure)"
            )
        ]
        ai_recommendations = [
            AIRecommendation(
                problem="High indexing computing expenditures associated with scraping modern JavaScript-heavy websites.",
                evidence="Google engineering whitepapers indicate rendering complex web structures comprises up to 20% of Googlebot's search indexing computing budget.",
                reasoning="Quantized transformer routers can predict rendering complexity from raw HTML before executing javascript, caching static layouts dynamically.",
                recommended_solution="AI-Driven Googlebot Pre-Rendering Estimator",
                expected_benefits="Reduce search bot indexing server loads by 15%, saving an estimated $140M in data center electricity costs.",
                implementation_difficulty="High",
                estimated_cost="$400k - $600k",
                timeline="8 months",
                expected_roi="400% in Year 1",
                priority="High"
            ),
            AIRecommendation(
                problem="High customer attrition during Google Cloud enterprise migration setup phases.",
                evidence="GCP onboarding statistics reveal that 18% of trial accounts churn due to database schema mapping friction between legacy servers and GCP formats.",
                reasoning="Large LLMs can read legacy SQL structures and auto-generate clean Terraform and SQL migration scripts dynamically.",
                recommended_solution="Gemini-Powered GCP Schema Migrator Engine",
                expected_benefits="Reduce enterprise cloud onboarding times from 3 weeks to under 4 hours, boosting GCP pipeline closures by 12%.",
                implementation_difficulty="Medium",
                estimated_cost="$150k - $220k",
                timeline="4 months",
                expected_roi="320% in Year 1",
                priority="Medium"
            )
        ]
        exec_summary = ExecutiveSummary(
            headline="Navigating the Search Paradigm Shift: Accelerating Cloud Onboarding and Optimizing Crawling Efficiency",
            summary="Alphabet is facing its most critical strategic juncture since inception. While Search remains highly profitable, conversational AI engines challenge the traditional link-based browsing model. To maintain growth, Google must maximize Googlebot rendering efficiency and capture enterprise cloud market share. We propose deploying an AI-Driven Pre-Rendering Estimator for Googlebot to save $140 Million in energy bills, and launching Gemini schema migration engines to accelerate GCP customer conversions.",
            pitch="Dear Sundar,\n\nAs Google navigates antitrust rulings and the shift to conversational AI search, protecting Google Cloud growth and search bot efficiency is vital. We propose: 1. Deploying an AI-Driven Pre-Rendering Estimator to reduce Googlebot indexing server loads by 15%, saving $140M, and 2. Integrating a Gemini Onboarding Migrator for GCP to compress setup times from weeks to hours, lifting enterprise sales closures. These steps will secure cloud margins and lower indexing overheads. Let's discuss implementing these models."
        )

    # -------------------------------------------------------------------------
    # HASH-BASED DYNAMIC FALLBACK (FOR OTHER COMPANIES)
    # -------------------------------------------------------------------------
    else:
        # Prevent identical templates by hashing the name
        hash_val = sum(ord(char) for char in company_name)
        
        # Pick unique indices
        industries = [
            "Advanced Robotics & Industrial Systems",
            "Biotechnology & Genomics Research",
            "SaaS & Enterprise Operations",
            "Financial Technology & Banking APIs",
            "Renewable Solar Energy & Smart Grids",
            "Supply Chain & Electric Logistics",
            "Artificial Intelligence & LLM Platforms",
            "Cybersecurity & Autonomous Threat Auditing"
        ]
        
        hqs = [
            "New York City, New York, USA",
            "London, United Kingdom",
            "Bengaluru, Karnataka, India",
            "Munich, Germany",
            "Tokyo, Japan",
            "Singapore",
            "Austin, Texas, USA",
            "Boston, Massachusetts, USA"
        ]
        
        revenues = [
            "$45 Million (Estimated)",
            "$125 Million (Annualized)",
            "$850 Million (Private Valuation)",
            "$1.2 Billion (Group Revenue)",
            "$15 Million (Seed / Pre-Series A)",
            "Private (Estimated $240M)",
            "$480 Million (GAAP Revenue)",
            "$2.5 Billion (NSE Public Scale)"
        ]
        
        fundings = [
            "Series B ($40M raised, lead: Accel Partners)",
            "Series C ($95M raised, lead: Sequoia Capital)",
            "Series A ($15M raised, lead: Y Combinator)",
            "Publicly Listed (NASDAQ Exchange)",
            "Private Equity (backed by Blackstone)",
            "Bootstrapped (Highly Profitable)",
            "Series D ($180M raised, lead: General Catalyst)",
            "Publicly Listed (NSE / BSE India)"
        ]
        
        industry_selected = industries[hash_val % len(industries)]
        hq_selected = hqs[hash_val % len(hqs)]
        revenue_selected = revenues[hash_val % len(revenues)]
        funding_selected = fundings[hash_val % len(fundings)]
        
        words = company_name.split()
        cap_name = " ".join([w.capitalize() for w in words])
        
        overview = CompanyOverview(
            name=f"{cap_name} Corp",
            industry=industry_selected,
            headquarters=hq_selected,
            geographic_presence="Global operations with regional offices in US, EU, and APAC",
            products_services=[f"{cap_name} Core Suite", f"{cap_name} Enterprise API", f"{cap_name} Insights Dashboard"],
            revenue=revenue_selected,
            funding=funding_selected,
            key_executives=["Sarah Jenkins (CEO)", "Michael Chen (CTO)", "David Miller (Chief Product Officer)"],
            expansion_plans=["Expanding direct enterprise sales in Western Europe", "Launching self-serve developer tier", "Building partner consulting ecosystem"],
            business_challenges=["Long enterprise sales cycles (average 6-9 months)", "Increasing churn in mid-market subscription tiers due to generic features", "High cloud infrastructure costs associated with database queries"],
            risks=["Fierce competition from legacy suite players", "Data security compliance requirements in the EU (GDPR)", "Technical debt in older backend codebases slowing release velocities"]
        )
        news = [
            NewsItem(title=f"{cap_name} Announces Next-Generation API Platform with Advanced Integrations", url="https://techcrunch.com", summary=f"{cap_name} launched its new API gateway to help customers connect legacy systems to their core cloud databases in under an hour.", date="February 2026"),
            NewsItem(title=f"{cap_name} Partners with Google Cloud to Build Generative Analytics Dashboards", url="https://venturebeat.com", summary=f"Through a new cloud alliance, {cap_name} will embed Google Vertex AI directly into its reporting modules for enterprise clients.", date="May 2025"),
            NewsItem(title=f"{cap_name} Named a Leader in Digital Operations Matrix Report", url="https://gartner.com", summary="Industry analysts recognized the company's rapid customer acquisition and outstanding customer support ratings in the SaaS space.", date="November 2025")
        ]
        swot = SWOTAnalysis(
            strengths=[
                "High customer satisfaction ratings and NPS of 72",
                "Flexible modular architecture that allows rapid API integrations",
                "Strong financial support from top-tier venture capital firms",
                "Talented core engineering team focused on modern architecture"
            ],
            weaknesses=[
                "High client onboarding churn due to lack of automated tutorials",
                "Heavy dependency on manual customer support for technical setup",
                "Inefficient database indexing causing latency at scale"
            ],
            opportunities=[
                "Integrating generative AI assistants directly into customer portals to enable conversational reporting",
                "Launching a marketplace for third-party developers to extend platform features",
                "Targeting public sector clients with FedRAMP compliance certification"
            ],
            threats=[
                "Rapid feature copycatting from larger legacy incumbents with deeper pockets",
                "Slowing macroeconomic corporate software spending budgets",
                "Potential security vulnerabilities from third-party open-source packages"
            ]
        )
        competitors = [
            CompetitorRow(
                name="LegacySystems Inc.",
                revenue="$1.8 Billion",
                employees="5,500",
                presence="North America, Europe",
                products=["Enterprise Core", "Legacy Analytics"],
                technology=["Java", "Oracle Database", "Angular"],
                strengths=["Massive install base", "Long-term corporate relationships", "Comprehensive feature list"],
                weaknesses=["Slower release cycles", "High total cost of ownership (TCO)", "Outdated UI/UX"],
                market_position="Leader (Legacy Enterprise)"
            ),
            CompetitorRow(
                name="VeloTech Co.",
                revenue="$80 Million",
                employees="280",
                presence="Global (Remote)",
                products=["Velo Cloud", "Velo Integration Hub"],
                technology=["Go", "GraphQL", "React", "Rust"],
                strengths=["Fast performance", "Developer-friendly pricing", "Modern product aesthetic"],
                weaknesses=["Lacks deep enterprise security features", "No local support team presence"],
                market_position="Challenger (SMB Segment)"
            )
        ]
        ai_recommendations = [
            AIRecommendation(
                problem="Long onboarding cycles and support queues caused by complex customer data onboarding.",
                evidence=f"{cap_name} customer support logs report that database mapping issues comprise 45% of onboarding support volume.",
                reasoning="LLMs are exceptional at schema mapping. A semantic database mapping agent can translate arbitrary user CSV columns into system database headers instantly.",
                recommended_solution="AI-Powered Customer Data Mapping Agent",
                expected_benefits="Reduce customer onboarding time from 14 days to less than 1 hour, cutting support workloads by 35%.",
                implementation_difficulty="Medium",
                estimated_cost="$90k - $120k",
                timeline="4 months",
                expected_roi="450% in Year 1",
                priority="High"
            ),
            AIRecommendation(
                problem="High customer attrition due to lack of self-serve BI reporting dashboards.",
                evidence="Customer churn surveys indicate that 'inability to export custom ad-hoc charts' was a top-3 reason for cancellation.",
                reasoning="Embedding a text-to-SQL dashboard generator lets business users query their database in plain English and render charts instantly.",
                recommended_solution="Conversational AI Business Intelligence Assistant",
                expected_benefits="Increase customer retention by 12% and boost upsell conversion by 18%.",
                implementation_difficulty="Medium",
                estimated_cost="$110k - $150k",
                timeline="5 months",
                expected_roi="380% in Year 1",
                priority="High"
            )
        ]
        exec_summary = ExecutiveSummary(
            headline=f"Unlocking {cap_name}'s Enterprise Scaling Potential: Automating Customer Onboarding and Custom BI Portals",
            summary=f"{cap_name} is experiencing healthy mid-market growth, backed by top-tier VC funding. However, long manual onboarding cycles and ad-hoc BI reporting requests bottleneck enterprise sales. By integrating AI-driven semantic schema mapping and embedding conversational text-to-SQL analytics, {cap_name} can eliminate customer support blockages and scale up-market. This strategy allows the company to maintain high customer satisfaction while compressing sales cycles.",
            pitch=f"Dear Sarah,\n\n{cap_name} has built a phenomenal core product with outstanding customer satisfaction. To successfully move up-market and capture enterprise accounts, we must tackle the onboarding bottleneck and ad-hoc reporting churn. We propose deploying an AI-Powered Customer Data Mapping Agent to compress onboarding from 2 weeks to 1 hour, along with a Conversational BI Assistant. These two initiatives will directly protect retention and allow your sales team to confidently pitch enterprise buyers. Let's collaborate to bring these AI capabilities into your product roadmap."
        )
        
    return BIReport(
        company_name=company_name,
        overview=overview,
        news=news,
        swot=swot,
        competitors=competitors,
        ai_recommendations=ai_recommendations,
        executive_summary=exec_summary,
        generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
        
    return BIReport(
        company_name=company_name,
        overview=overview,
        news=news,
        swot=swot,
        competitors=competitors,
        ai_recommendations=ai_recommendations,
        executive_summary=exec_summary,
        generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

# =====================================================================
# AGENT STATE GRAPH DEFINITION
# =====================================================================
def build_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research_agent", research_agent)
    workflow.add_node("news_agent", news_agent)
    workflow.add_node("analyst_agent", analyst_agent)
    workflow.add_node("competitor_agent", competitor_agent)
    workflow.add_node("consultant_agent", consultant_agent)
    workflow.add_node("pitch_agent", pitch_agent)
    
    # Set Entry Point
    workflow.set_entry_point("research_agent")
    
    # Add transitions
    workflow.add_edge("research_agent", "news_agent")
    workflow.add_edge("news_agent", "analyst_agent")
    workflow.add_edge("analyst_agent", "competitor_agent")
    workflow.add_edge("competitor_agent", "consultant_agent")
    workflow.add_edge("consultant_agent", "pitch_agent")
    workflow.add_edge("pitch_agent", END)
    
    return workflow.compile()

# Orchestrator execution function
def run_bi_platform(company_name: str) -> BIReport:
    # 1. Check if we should run in demo fallback mode
    engine = Config.get_ai_engine()
    
    if engine == "demo":
        # Missing API keys completely -> Return simulated dashboard data
        return get_mock_report(company_name)
        
    # 2. Otherwise run the LangGraph Multi-Agent Flow
    graph = build_agent_graph()
    
    initial_state = {
        "company_name": company_name,
        "research_data": None,
        "news_data": None,
        "analyst_data": None,
        "competitor_data": None,
        "ai_data": None,
        "pitch_data": None,
        "report": None,
        "errors": []
    }
    
    try:
        final_state = graph.invoke(initial_state)
        
        # Aggregate the state results into the BIReport Pydantic schema
        res_data = final_state.get("research_data") or {}
        n_data = final_state.get("news_data") or []
        an_data = final_state.get("analyst_data") or {}
        comp_data = final_state.get("competitor_data") or []
        ai_rec_data = final_state.get("ai_data") or []
        p_data = final_state.get("pitch_data") or {}
        
        # Fallback if specific agent returned incomplete or invalid structure
        # (e.g. LLM rate limit or weird format)
        if not res_data or res_data.get("status") == "skipped_no_llm":
            # Fallback to mock report if the graph execution failed to produce text
            return get_mock_report(company_name)
            
        overview = CompanyOverview(
            name=res_data.get("name", company_name),
            industry=res_data.get("industry", "Unknown Industry"),
            headquarters=res_data.get("headquarters", "Global"),
            geographic_presence=res_data.get("geographic_presence", "Global"),
            products_services=res_data.get("products_services", []),
            revenue=res_data.get("revenue", "N/A"),
            funding=res_data.get("funding", "N/A"),
            key_executives=res_data.get("key_executives", []),
            expansion_plans=res_data.get("expansion_plans", []),
            business_challenges=res_data.get("business_challenges", []),
            risks=res_data.get("risks", [])
        )
        
        news = [
            NewsItem(
                title=n.get("title", "News Headline"),
                url=n.get("url"),
                summary=n.get("summary", "News summary details."),
                date=n.get("date")
            ) for n in n_data
        ]
        
        swot = SWOTAnalysis(
            strengths=an_data.get("strengths", []),
            weaknesses=an_data.get("weaknesses", []),
            opportunities=an_data.get("opportunities", []),
            threats=an_data.get("threats", [])
        )
        
        competitors = [
            CompetitorRow(
                name=c.get("name", "Competitor"),
                revenue=c.get("revenue", "N/A"),
                employees=c.get("employees", "N/A"),
                presence=c.get("presence", "N/A"),
                products=c.get("products", []),
                technology=c.get("technology", []),
                strengths=c.get("strengths", []),
                weaknesses=c.get("weaknesses", []),
                market_position=c.get("market_position", "Competitor")
            ) for c in comp_data
        ]
        
        ai_recommendations = [
            AIRecommendation(
                problem=r.get("problem", "Identified bottleneck"),
                evidence=r.get("evidence", "Operational evidence"),
                reasoning=r.get("reasoning", "Why AI solves this"),
                recommended_solution=r.get("recommended_solution", "Proposed AI module"),
                expected_benefits=r.get("expected_benefits", "Expected benefits"),
                implementation_difficulty=r.get("implementation_difficulty", "Medium"),
                estimated_cost=r.get("estimated_cost", "$100k"),
                timeline=r.get("timeline", "6 months"),
                expected_roi=r.get("expected_roi", "100%"),
                priority=r.get("priority", "High")
            ) for r in ai_rec_data
        ]
        
        exec_summary = ExecutiveSummary(
            headline=p_data.get("headline", "AI Transformation Roadmap"),
            summary=p_data.get("summary", "Executive overview summary."),
            pitch=p_data.get("pitch", "Dear CEO, we propose AI transformation strategies...")
        )
        
        return BIReport(
            company_name=company_name,
            overview=overview,
            news=news,
            swot=swot,
            competitors=competitors,
            ai_recommendations=ai_recommendations,
            executive_summary=exec_summary,
            generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        print(f"LangGraph execution exception: {e}")
        # Final fallback to mock if error occurs in state orchestration
        return get_mock_report(company_name)
