# evaluator.py
from ai_engine import match_semantic_compliance

def evaluate_financials(extracted_bidder_turnover, required_turnover):
    """Deterministic math check. No AI allowed."""
    try:
        bidder_val = int(extracted_bidder_turnover)
        req_val = int(required_turnover)
        
        if bidder_val >= req_val:
            return {"status": "Eligible", "reason": f"{bidder_val} meets requirement of {req_val}"}
        else:
            return {"status": "Not Eligible", "reason": f"Turnover {bidder_val} is less than {req_val}"}
    except ValueError:
        return {"status": "Needs Manual Review", "reason": "Could not parse turnover as a valid number."}

def check_compliance_rule(bidder_text, rule):
    """Uses DeBERTa but forces human review if unsure."""
    ai_result = match_semantic_compliance(bidder_text, rule)
    
    if ai_result["confidence"] < 0.85 or ai_result["label"] == "neutral":
        return {"status": "Needs Manual Review", "reason": "Ambiguous wording. Confidence too low."}
    elif ai_result["label"] == "entailment":
        return {"status": "Eligible", "reason": "Compliance confirmed."}
    else:
        return {"status": "Not Eligible", "reason": "Document contradicts requirement."}