import io
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.schemas import BIReport
from app.agents.graph import run_bi_platform
from app.utils.pdf_generator import generate_pdf_report
from app.utils.ppt_generator import generate_ppt_report

app = FastAPI(
    title="AI Business Intelligence & Research Consultant API",
    description="Multi-Agent Corporate BI Agent System",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RECENT_SEARCHES_FILE = "recent_searches.json"

def get_recent_searches():
    if os.path.exists(RECENT_SEARCHES_FILE):
        try:
            with open(RECENT_SEARCHES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def add_recent_search(company_name: str):
    searches = get_recent_searches()
    # Normalize
    name = company_name.strip()
    if name in searches:
        searches.remove(name)
    searches.insert(0, name)
    # Limit to top 10
    searches = searches[:10]
    try:
        with open(RECENT_SEARCHES_FILE, "w") as f:
            json.dump(searches, f)
    except Exception as e:
        print(f"Error saving recent searches: {e}")

@app.get("/api/recent")
def get_recent():
    """Retrieve history of recent searches."""
    return get_recent_searches()

@app.post("/api/search", response_model=BIReport)
async def search_company(payload: dict):
    """
    Triggers the Multi-Agent Business Intelligence pipeline for the given company.
    """
    company_name = payload.get("company_name", "").strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name is required")
    
    # Run the platform pipeline (live agents or fallback mock generator)
    report = run_bi_platform(company_name)
    
    # Save search to history
    add_recent_search(company_name)
    
    return report

@app.post("/api/export/pdf")
async def export_pdf(report: BIReport):
    """
    Exports the generated BIReport object into a styled corporate PDF document.
    """
    try:
        pdf_buffer = io.BytesIO()
        generate_pdf_report(report, pdf_buffer)
        pdf_buffer.seek(0)
        
        filename = f"{report.company_name.lower().replace(' ', '_')}_bi_report.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.post("/api/export/ppt")
async def export_ppt(report: BIReport):
    """
    Exports the generated BIReport object into a styled corporate PowerPoint presentation.
    """
    try:
        ppt_buffer = io.BytesIO()
        generate_ppt_report(report, ppt_buffer)
        ppt_buffer.seek(0)
        
        filename = f"{report.company_name.lower().replace(' ', '_')}_presentation.pptx"
        
        return StreamingResponse(
            ppt_buffer,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"PPTX generation failed: {str(e)}")

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AI BI Platform API"}
