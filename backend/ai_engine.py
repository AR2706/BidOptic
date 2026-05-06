# ai_engine.py
from transformers import pipeline

# 1. Flan-T5 for Information Extraction
# Using 'small' or 'base' for faster hackathon testing
ie_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

def extract_financial_rule(tender_text):
    prompt = f"Extract the minimum required turnover in Rupees from this text. Only return the number:\n\n{tender_text}"
    result = ie_pipeline(prompt, max_length=50)
    return result[0]['generated_text']

# 2. DeBERTa for Natural Language Inference (Compliance Matching)
nli_pipeline = pipeline("zero-shot-classification", model="cross-encoder/nli-deberta-v3-base")

def match_semantic_compliance(bidder_text, tender_rule):
    labels = ["entailment", "contradiction", "neutral"]
    template = "This document confirms that {} matches the requirement: " + tender_rule
    
    result = nli_pipeline(bidder_text, candidate_labels=labels, hypothesis_template=template)
    
    top_label = result['labels'][0]
    confidence = result['scores'][0]
    
    return {"label": top_label, "confidence": confidence}