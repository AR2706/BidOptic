import os
import re
import json
import requests
import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 1. Load variables from .env (Local) or Environment (Render)
load_dotenv()

app = FastAPI(title="BidOptic AI Engine")

# 2. CORS Middleware
# Allows your frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your specific frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. AI Configuration
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = os.getenv("HF_MODEL")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_hf(payload):
    """Utility to query Hugging Face Inference API"""
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# 4. ROUTES

@app.get("/")
async def root():
    """
    Health check route. 
    Visiting the URL in image_68bef0.png will now show this instead of 'Not Found'.
    """
    return {
        "status": "online",
        "message": "BidOptic Backend is fully operational.",
        "version": "2.0.1"
    }

@app.post("/upload-tender/")
async def upload_tender(file: UploadFile = File(...), criteria: str = Form("")):
    # Read PDF text
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = "\n".join([page.get_text() for page in doc])
    
    # Process comma or newline separated rules
    rules_list = [r.strip() for r in re.split(r'[,\n]+', criteria) if r.strip()]
    results = []

    for index, rule in enumerate(rules_list):
        evidence_list = []
        
        # Step A: Pattern Matching for Multi-Source Extraction
        # Finds every mention of the requirement in the document
        search_pattern = re.compile(re.escape(rule), re.IGNORECASE)
        matches = list(search_pattern.finditer(full_text))
        
        if matches:
            status_type = "pass"
            # Get up to 5 unique evidence snippets
            for m in matches[:5]:
                start = max(0, m.start() - 80)
                end = min(len(full_text), m.end() + 120)
                snippet = full_text[start:end].replace('\n', ' ').strip()
                evidence_list.append(f"...{snippet}...")
        else:
            status_type = "fail"
            evidence_list = [f"No textual match found for '{rule}' in the tender."]

        # Step B: AI Semantic Verification
        try:
            prompt = f"<|user|>\nAnalyze this text: {full_text[:2000]}\nRule: {rule}\nDoes it pass? Return ONLY JSON: {{\"status\": \"pass\", \"reason\": \"...\"}}<|end|>\n<|assistant|>"
            ai_out = query_hf({"inputs": prompt})
            ai_text = ai_out[0]['generated_text'] if isinstance(ai_out, list) else str(ai_out)
            match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            ai_data = json.loads(match.group()) if match else {}
            final_reason = ai_data.get("reason", evidence_list[0])
        except:
            final_reason = evidence_list[0]

        results.append({
            "id": index + 1,
            "type": status_type,
            "title": f"Verified ({len(matches)} Sources)" if status_type == "pass" else "Non-Compliant",
            "confidence": "Hybrid Scan",
            "rule": rule,
            "found": final_reason,
            "all_evidence": evidence_list
        })

    return {"status": "success", "results": results}

@app.get("/")
def home():
    return {"message": "BidOptic AI API is running!"}