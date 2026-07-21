from typing import TypedDict, List, Optional, Any
from app.schemas import BIReport

class AgentState(TypedDict):
    company_name: str
    research_data: Optional[Any]
    news_data: Optional[Any]
    analyst_data: Optional[Any]
    competitor_data: Optional[Any]
    ai_data: Optional[Any]
    pitch_data: Optional[Any]
    report: Optional[BIReport]
    errors: List[str]
