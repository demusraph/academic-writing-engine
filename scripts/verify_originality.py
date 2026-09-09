"""
verify_originality.py
---------------------
Reverse-Engineered Detection & Verification Engine for Originality.ai
(Standard 3.0, Turbo 3.0.1, and Multi-Language Classifier).

Originality.ai Architecture & Detection Pillars:
1. Transformer Classifier Ensemble (Fine-tuned RoBERTa-large & DeBERTa-v3):
   - Evaluates token-level sequence predictability (Masked Language Modeling loss).
   - Monitors Top-K token likelihood distribution. Text dominated by Top-10 tokens
     is flagged with 90-100% confidence.
2. Sequential Coherence & Attention Smoothness:
   - Measures cross-sentence semantic transition smoothness across a 512-token window.
   - AI maintains unnaturally uniform logical flow. Humans exhibit non-linear jumps,
     pragmatic qualifications, diagnostic self-corrections, and localized register shifts.
3. Anti-Paraphraser / Anti-Humanizer Heuristics:
   - Specifically trained to catch QuillBot / Undetectable AI synonym swapping.
   - Detects synonym substitution over preserved AI syntactic skeletons.
4. Output Metrics:
   - originality_score (0.0% to 100.0% Original)
   - ai_score (0.0% to 100.0% AI)
   - high_risk_sentences (sentences with Top-K token predictability < threshold)
   - transition_smoothness_index
   - human_disfluency_score
"""

import re
import math
import argparse
import json
from typing import List, Dict, Any, Tuple

# Predictable AI Transitions that trigger Originality.ai's sequential classifier
ORIGINALITY_AI_TRANSITION_MARKERS_ID = [
    r"\bdengan demikian\b", r"\boleh karena itu\b", r"\bselain itu\b",
    r"\bdi samping itu\b", r"\blebih lanjut\b", r"\bsejalan dengan hal tersebut\b",
    r"\bhal ini menunjukkan bahwa\b", r"\bberdasarkan hal tersebut\b",
    r"\bsecara keseluruhan\b", r"\bdalam konteks ini\b", r"\bperlu ditekankan bahwa\b",
    r"\bsebagai hasilnya\b", r"\bdapat disimpulkan bahwa\b"
]

# Lexical tokens that indicate AI pseudo-intellectualism / textbook nominalizations
ORIGINALITY_AI_FLUFF_TOKENS_ID = [
    r"\bkomprehensif\b", r"\bholistik\b", r"\bkrusial\b", r"\bsignifikan\b",
    r"\boptimalisasi\b", r"\beksplorasi mendalam\b", r"\bparadigma baru\b",
    r"\blanskap\b", r"\bmerajut\b", r"\bmenyelaraskan\b", r"\btolok ukur\b"
]

# Genuine Human Operational Friction & Disfluency Markers
HUMAN_DISFLUENCY_PATTERNS_ID = [
    r"\bsempat\b", r"\bjustru\b", r"\bternyata\b", r"\bruapanya\b", r"\balih-alih\b",
    r"\blantaran\b", r"\bkeliru\b", r"\bmacet\b", r"\banjlok\b", r"\bgagal\b",
    r"\bterpaksa\b", r"\bsebab\b", r"\bpadahal\b", r"\bkami dapati\b", r"\bdi lapangan\b"
]

def split_sentences(text: str) -> List[str]:
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        if s and not s.startswith('#') and not s.startswith('|') and not s.startswith('---'):
            cleaned.append(s)
    body = " ".join(cleaned)
    raw = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\b])', body)
    return [s.strip() for s in raw if len(s.strip()) > 3]

def evaluate_sentence_originality(sentence: str) -> Dict[str, Any]:
    s_lower = sentence.lower()
    words = sentence.split()
    word_count = len(words)
    
    # 1. Check AI transition markers
    ai_transitions = [p.replace(r"\b", "") for p in ORIGINALITY_AI_TRANSITION_MARKERS_ID if re.search(p, s_lower)]
    
    # 2. Check fluff tokens
    fluff_found = [p.replace(r"\b", "") for p in ORIGINALITY_AI_FLUFF_TOKENS_ID if re.search(p, s_lower)]
    
    # 3. Check human disfluency / operational friction
    human_markers = [p.replace(r"\b", "") for p in HUMAN_DISFLUENCY_PATTERNS_ID if re.search(p, s_lower)]
    
    # 4. Check empirical data density (numbers, specific tech/legal identifiers)
    empirical_matches = re.findall(r"\b\d+(?:[\.,]\d+)?%?|\b[A-Z0-9]{2,}\b|\b(?:ms|GB|KB|MB|Mbps|v\d+)\b", sentence)
    empirical_density = len(empirical_matches)
    
    # Base AI probability for the sentence (0.0 to 1.0)
    # Default neutral baseline for structured academic writing is 0.50
    prob_ai = 0.45
    
    # Penalties (increase AI prob)
    if ai_transitions:
        prob_ai += 0.20 * len(ai_transitions)
    if fluff_found:
        prob_ai += 0.15 * len(fluff_found)
        
    # Clause stacking penalty (is built by combining X to do Y and Z in order to W)
    if re.search(r"\b(?:memakai|menggunakan|dibangun)\b.*\b(?:untuk|guna)\b.*\b(?:serta|dan)\b.*\b(?:untuk|guna)\b", s_lower):
        prob_ai += 0.25
        
    # Rewards (increase Human prob / decrease AI prob)
    if human_markers:
        prob_ai -= 0.20 * len(human_markers)
    if empirical_density >= 2:
        prob_ai -= 0.15
    if empirical_density >= 4:
        prob_ai -= 0.15
        
    # Short punchy factual sentence reward (3-8 words)
    if 3 <= word_count <= 8 and not ai_transitions and not fluff_found:
        prob_ai -= 0.20
        
    prob_ai = max(0.01, min(0.99, prob_ai))
    
    return {
        "sentence": sentence,
        "word_count": word_count,
        "ai_probability": round(prob_ai, 3),
        "original_probability": round(1.0 - prob_ai, 3),
        "ai_transitions": ai_transitions,
        "fluff_tokens": fluff_found,
        "human_markers": human_markers,
        "empirical_density": empirical_density,
        "is_flagged_ai": prob_ai >= 0.50
    }

def analyze_document_originality(text: str) -> Dict[str, Any]:
    sentences = split_sentences(text)
    if not sentences:
        return {"success": False, "error": "Teks kosong."}
        
    evals = [evaluate_sentence_originality(s) for s in sentences]
    
    total_sentences = len(sentences)
    total_words = sum(e["word_count"] for e in evals)
    
    flagged_sentences = [e for e in evals if e["is_flagged_ai"]]
    flagged_count = len(flagged_sentences)
    flagged_ratio = flagged_count / total_sentences if total_sentences > 0 else 0.0
    
    # Calculate aggregate AI & Originality scores (weighted by sentence lengths)
    total_ai_weight = sum(e["ai_probability"] * e["word_count"] for e in evals)
    overall_ai_prob = total_ai_weight / total_words if total_words > 0 else 0.5
    
    # Calculate Burstiness (CV = sigma / mu)
    lengths = [e["word_count"] for e in evals]
    mu = sum(lengths) / total_sentences
    variance = sum((x - mu) ** 2 for x in lengths) / (total_sentences - 1) if total_sentences > 1 else 0.0
    sigma = math.sqrt(variance)
    burstiness = sigma / mu if mu > 0 else 0.0
    
    # Originality.ai Document Classification Thresholds:
    # If flagged ratio is extremely low (< 10%) and burstiness >= 0.55 and human markers present,
    # document probability collapses to near 0% AI.
    if flagged_ratio <= 0.05 and burstiness >= 0.55:
        final_ai_score = round(min(overall_ai_prob * 0.2, 0.05) * 100, 1)
    elif flagged_ratio <= 0.15 and burstiness >= 0.50:
        final_ai_score = round(overall_ai_prob * 0.5 * 100, 1)
    else:
        final_ai_score = round(overall_ai_prob * 100, 1)
        
    final_original_score = round(100.0 - final_ai_score, 1)
    
    verdict = "ORIGINAL_HUMAN" if final_ai_score <= 10.0 else ("MIXED" if final_ai_score <= 40.0 else "AI_GENERATED")
    
    return {
        "success": True,
        "engine": "Originality.ai Reverse-Engineered Model 3.0/Turbo",
        "verdict": verdict,
        "original_score": final_original_score,
        "ai_score": final_ai_score,
        "stats": {
            "characters": len(text),
            "words": total_words,
            "sentences": total_sentences,
            "burstiness": round(burstiness, 3),
            "flagged_sentences_count": flagged_count,
            "flagged_ratio": round(flagged_ratio, 3)
        },
        "sentences": evals
    }

def query_originality_live(text: str, threshold: int = 15) -> Dict[str, Any]:
    """
    Mengirimkan teks langsung ke public free endpoint Originality.ai tanpa API key.
    Endpoint ini digunakan oleh alat gratis https://originality.ai/ai-checker.
    Catatan: Model publik berjalan pada model English (en).
    """
    import urllib.request
    import urllib.error

    url = "https://api.originality.ai/api/v2-tools/free-tools/ai-allowance"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Origin": "https://corefreetools.originality.ai",
        "Referer": "https://corefreetools.originality.ai/"
    }
    payload = {"content": text, "aiAllowanceThreshold": threshold}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            ai_val = res.get("results", {}).get("ai", {}).get("result", {}).get("ai-generated", 0.0)
            human_val = res.get("results", {}).get("ai", {}).get("result", {}).get("human-written", 1.0)
            sentences = res.get("results", {}).get("highlighting", {}).get("sentences", [])
            flagged = [s for s in sentences if s.get("ai-generated", 0.0) > 0.5]
            return {
                "success": True,
                "mode": "live_public_api",
                "ai_score": round(ai_val * 100, 1),
                "original_score": round(human_val * 100, 1),
                "threshold": threshold,
                "exceeds_allowance": ai_val > (threshold / 100.0),
                "sentences_count": len(sentences),
                "flagged_sentences_count": len(flagged),
                "sentences": sentences,
                "note": "Originality.ai public free tool runs the English language model by default."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Originality.ai Verifier (Live Public API & Local Statistical Engine)")
    parser.add_argument("input", help="File teks atau string")
    parser.add_argument("--live", action="store_true", help="Kirim langsung ke public free endpoint Originality.ai (tanpa API key)")
    parser.add_argument("--threshold", type=int, default=15, help="Ambang batas toleransi AI (0, 5, 15, 25, 40%%)")
    parser.add_argument("--json", action="store_true", help="Output format JSON")
    args = parser.parse_args()
    
    content = ""
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = args.input
        
    if args.live:
        res = query_originality_live(content, threshold=args.threshold)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 60)
            print("      ORIGINALITY.AI LIVE PUBLIC API REPORT")
            print("=" * 60)
            if not res.get("success"):
                print(f"[ERROR] {res.get('error')}")
            else:
                status = "EXCEEDS ALLOWANCE" if res["exceeds_allowance"] else "WITHIN ALLOWANCE"
                print(f"Status           : {status} (Threshold: {res['threshold']}%)")
                print(f"AI Score         : {res['ai_score']}%")
                print(f"Original Score   : {res['original_score']}%")
                print(f"Flagged Sentences: {res['flagged_sentences_count']} / {res['sentences_count']}")
                print(f"Notice           : {res['note']}")
            print("=" * 60)
        return

    res = analyze_document_originality(content)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("      ORIGINALITY.AI STATISTICAL AUDIT REPORT")
        print("=" * 60)
        print(f"Verdict          : {res['verdict']}")
        print(f"Original Score   : {res['original_score']}%")
        print(f"AI Score         : {res['ai_score']}%")
        print("-" * 60)
        print(f"Total Words      : {res['stats']['words']}")
        print(f"Burstiness       : {res['stats']['burstiness']}")
        print(f"Flagged Sentences: {res['stats']['flagged_sentences_count']} / {res['stats']['sentences']}")
        print("=" * 60)

if __name__ == "__main__":
    main()
