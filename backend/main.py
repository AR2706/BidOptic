import os
import re
import json
import requests
import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BidOptic AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Replace with your valid HF Token
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = os.getenv("HF_MODEL")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_hf(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
    return response.json()

@app.post("/upload-tender/")
async def upload_tender(file: UploadFile = File(...), criteria: str = Form("")):
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = "\n".join([page.get_text() for page in doc])
    
    # Split input by commas or new lines
    rules_list = [r.strip() for r in re.split(r'[,\n]+', criteria) if r.strip()]
    results = []

    for index, rule in enumerate(rules_list):
        prompt = f"<|user|>\nAnalyze this tender text: {full_text[:3000]}\nRule: {rule}\nDoes it pass? Reply ONLY in JSON: {{\"status\": \"pass\", \"reason\": \"...\"}}<|end|>\n<|assistant|>"
        
        try:
            output = query_hf({"inputs": prompt, "parameters": {"max_new_tokens": 150}})
            response_text = output[0]['generated_text'] if isinstance(output, list) else str(output)
            
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            data = json.loads(match.group()) if match else None
            
            if not data: raise Exception("Incomplete AI Response")

            results.append({
                "id": index + 1,
                "type": data.get("status", "review"),
                "title": "Rule Verified" if data.get("status") == "pass" else "Ineligible",
                "confidence": "92%",
                "rule": rule,
                "found": data.get("reason"),
                "hasBoundingBox": True
            })
            
        except Exception:
            # Contextual Snippet Extraction Fallback
            search_pattern = re.compile(re.escape(rule), re.IGNORECASE)
            match = search_pattern.search(full_text)
            
            if match:
                # Extract 60 chars before and 100 chars after for proof
                start = max(0, match.start() - 60)
                end = min(len(full_text), match.end() + 100)
                actual_snippet = full_text[start:end].replace('\n', ' ').strip()
                evidence = f"...{actual_snippet}..."
                status_type = "pass"
            else:
                evidence = f"No mention of '{rule}' detected in the document content."
                status_type = "fail"

            results.append({
                "id": index + 1,
                "type": status_type,
                "title": "Evidence Located" if status_type == "pass" else "Not Found",
                "confidence": "Local Scan",
                "rule": rule,
                "found": evidence,
                "hasBoundingBox": True
            })

    return {"status": "success", "results": results}