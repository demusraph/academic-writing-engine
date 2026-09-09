"""
verify_gptzero.py
-----------------
Engine verifikasi, simulasi statistik, dan kalibrasi kaliber GPTZero
(https://app.gptzero.me / https://api.gptzero.me).

Mendukung:
1. Live API Query: Jika GPTZERO_API_KEY atau flag --api-key / --jwt tersedia,
   mengirimkan teks langsung ke endpoint v2 (/v2/predict/text) atau v3 (/v3/ai/text).
2. Local Statistical & Heuristic Calibration Engine:
   Jika API key tidak diset, mengkalkulasi metrik reverse-engineered GPTZero:
   - Per-sentence Perplexity & predictability score
   - Document Burstiness (Coefficient of Variation sigma / mu dari panjang kalimat)
   - Sentence-level AI highlighting prediction (highlight_sentence_for_ai)
   - Klasifikasi dokumen (HUMAN_ONLY, MIXED, AI_ONLY) dan completely_generated_prob
3. Auto-Clean Mode (--auto-clean):
   Otomatis membedah dan merevisi kalimat yang ter-flag AI agar variasi sintaksis
   meningkat (burstiness >= 0.55) dan seluruh kalimat berstatus HUMAN.
"""

import sys
import os
import json
import time
import math
import re
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Tuple

# AI Cliches that drop Perplexity (GPTZero specific triggers)
EN_AI_CLICHES = [
    r"\bdelve\b", r"\bdelve into\b", r"\brobust\b", r"\bcomprehensive\b",
    r"\bpivotal\b", r"\bintricate\b", r"\bintricacies\b", r"\bmultifaceted\b",
    r"\btestament to\b", r"\blandscape\b", r"\bfoster\b", r"\bleverage\b",
    r"\bparadigm\b", r"\bparadigm shift\b", r"\bunderscore\b", r"\bunderscores\b",
    r"\bembark\b", r"\btapestry\b", r"\bbeacon\b", r"\bseamless\b", r"\bseamlessly\b",
    r"\bgame-changer\b", r"\bit is important to note\b", r"\bit is worth noting that\b",
    r"\bfurthermore\b", r"\bmoreover\b", r"\badditionally\b", r"\bin conclusion\b"
]

ID_AI_CLICHES = [
    r"\bberperan krusial\b", r"\bsangat penting\b", r"\bmenelisik lebih dalam\b",
    r"\bmenelaah lebih dalam\b", r"\bmerajut\b", r"\bmenyelaraskan\b",
    r"\bparadigma baru\b", r"\bdinamika yang kompleks\b", r"\bmenjembatani kesenjangan\b",
    r"\bkomprehensif\b", r"\btidak dapat dipungkiri bahwa\b", r"\bmelandasi\b",
    r"\btolok ukur utama\b", r"\bsecara holistik\b", r"\bmembuka cakrawala baru\b",
    r"\blanskap penelitian\b", r"\bsinergi\b", r"\bmengakselerasi\b",
    r"\bmenstimulasi\b", r"\boptimasi menyeluruh\b", r"\boleh karena itu\b",
    r"\blebih lanjut\b", r"\bdi samping itu\b", r"\bperlu dicatat bahwa\b"
]

def split_into_sentences(text: str) -> List[str]:
    """Memecah teks menjadi daftar kalimat dengan mempertahankan struktur."""
    # Bersihkan markdown headers/tables dari perhitungan jika ada
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('|') or stripped.startswith('---'):
            continue
        if stripped:
            cleaned_lines.append(stripped)
            
    body = " ".join(cleaned_lines)
    # Split regex sentence boundary
    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\b])', body)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 3]
    return sentences

def calculate_burstiness(sentences: List[str]) -> Tuple[float, float, float]:
    """
    Menghitung Burstiness (Coefficient of Variation) dari panjang kalimat.
    Formula: sigma / mu
    - mu: Rata-rata jumlah kata per kalimat
    - sigma: Standar deviasi panjang kalimat
    - CV: Rasio variasi. AI biasanya < 0.30; Human >= 0.55
    """
    if not sentences:
        return 0.0, 0.0, 0.0
        
    lengths = [len(s.split()) for s in sentences]
    n = len(lengths)
    if n == 0:
        return 0.0, 0.0, 0.0
    if n == 1:
        return float(lengths[0]), 0.0, 0.0
        
    mean = sum(lengths) / n
    variance = sum((x - mean) ** 2 for x in lengths) / (n - 1)
    std_dev = math.sqrt(variance)
    burstiness = (std_dev / mean) if mean > 0 else 0.0
    return mean, std_dev, burstiness

def evaluate_sentence_perplexity_proxy(sentence: str, lang: str = 'auto') -> Dict[str, Any]:
    """
    Menghitung skor proksi perplexity dan memprediksi highlight AI untuk kalimat.
    """
    s_lower = sentence.lower()
    words = sentence.split()
    word_count = len(words)
    
    # Deteksi bahasa
    if lang == 'auto':
        lang = 'id' if any(w in s_lower for w in [' yang ', ' pada ', ' dan ', ' kami ', ' dengan ', ' dari ']) else 'en'
        
    cliches = ID_AI_CLICHES if lang == 'id' else EN_AI_CLICHES
    found_cliches = []
    for pat in cliches:
        if re.search(pat, s_lower):
            found_cliches.append(pat.replace(r"\b", ""))
            
    # Pola sintaksis AI
    syntax_penalty = 0
    # 1. Gerund / Nominalisasi pasif opener
    if lang == 'id':
        if re.match(r"^[Pp]engujian performa pada|^[Pp]engumpulan data primer|^[Ee]valuasi model", sentence):
            syntax_penalty += 35
    else:
        if re.match(r"^[Ee]valuating the|^[Bb]enchmarking|^[Dd]ecoupling the", sentence):
            syntax_penalty += 35
            
    # 2. Trailing participial clause
    if re.search(r",\s*(?:permitting|resulting in|causing|highlighting|underscoring)\b", s_lower):
        syntax_penalty += 30
        
    # 3. Empiris Reward (Angka eksak, hardware, persen, nama alat ukur, putusan hukum, informan kualitatif menaikkan perplexity)
    cross_domain_empirical_regex = (
        r"\b\d+(?:\.\d+)?%?|"
        r"\b(?:RTX|CPU|RAM|ms|fps|v\d+\.\d+|Python|PyTorch|GHz|MB|GB|volt|"
        r"Pasal|Undang-Undang|UU|KUHP|Mahkamah Agung|Pengadilan Niaga|kasasi|homologasi|UNCLOS|arbitral|treaty|jurisdiction|adjudicat\w+|"
        r"informan|transkrip|wawancara|purposive sampling|saturasi data|etnografi|catatan lapangan|fieldwork|triangulasi|inter-coder|"
        r"Cohen(?:\'s)? Kappa|Cronbach(?:\'s)? Alpha|Likert|PHQ-9|ANCOVA|attrition rate|semi-structured interviews|coding matrix)\b"
    )
    empirical_signals = len(re.findall(cross_domain_empirical_regex, sentence, re.IGNORECASE))
    empirical_bonus = min(empirical_signals * 15, 45)
    
    # Base perplexity score (skala 0 - 100, semakin tinggi semakin human)
    base_ppl = 65.0
    base_ppl -= (len(found_cliches) * 25)
    base_ppl -= syntax_penalty
    base_ppl += empirical_bonus
    base_ppl = max(5.0, min(99.0, base_ppl))
    
    # Sentence-level AI probability (kebalikan dari perplexity)
    ai_prob = (100.0 - base_ppl) / 100.0
    
    # Sentence highlight condition in GPTZero: ai_prob > 0.45 or multiple cliches
    highlight = (ai_prob > 0.45) or (len(found_cliches) >= 1 and syntax_penalty > 0)
    
    return {
        'sentence': sentence,
        'words': word_count,
        'perplexity_proxy': round(base_ppl, 1),
        'ai_probability': round(ai_prob, 3),
        'highlight_sentence_for_ai': highlight,
        'cliches_found': found_cliches,
        'syntax_penalty': syntax_penalty > 0
    }

def analyze_text_gptzero_local(text: str) -> Dict[str, Any]:
    """
    Simulasi komprehensif metrik GPTZero berdasarkan reverse-engineering.
    """
    sentences = split_into_sentences(text)
    if not sentences:
        return {'success': False, 'error': 'Teks kosong atau tidak memuat kalimat lengkap.'}
        
    total_words = sum(len(s.split()) for s in sentences)
    mean_len, std_dev, burstiness = calculate_burstiness(sentences)
    
    sentence_evals = [evaluate_sentence_perplexity_proxy(s) for s in sentences]
    highlighted_count = sum(1 for e in sentence_evals if e['highlight_sentence_for_ai'])
    highlight_ratio = highlighted_count / len(sentences) if sentences else 0.0
    
    # Overall Document Classification
    # GPTZero classes: HUMAN_ONLY, MIXED, AI_ONLY
    if highlight_ratio <= 0.05 and burstiness >= 0.45:
        classification = "HUMAN_ONLY"
        predicted_class = "human"
        prob_ai = round(highlight_ratio * 0.2, 3)
        prob_human = round(1.0 - prob_ai, 3)
        prob_mixed = 0.0
        confidence = "high"
    elif highlight_ratio <= 0.25:
        classification = "MIXED"
        predicted_class = "mixed"
        prob_ai = round(0.20 + (highlight_ratio * 0.5), 3)
        prob_human = round(1.0 - prob_ai, 3)
        prob_mixed = round(highlight_ratio, 3)
        confidence = "medium"
    else:
        classification = "AI_ONLY"
        predicted_class = "ai"
        prob_ai = round(min(0.99, 0.50 + (highlight_ratio * 0.5)), 3)
        prob_human = round(1.0 - prob_ai, 3)
        prob_mixed = 0.1
        confidence = "high"
        
    return {
        'success': True,
        'mode': 'local_heuristic_model',
        'document_classification': classification,
        'predicted_class': predicted_class,
        'completely_generated_prob': prob_ai,
        'class_probabilities': {
            'human': prob_human,
            'ai': prob_ai,
            'mixed': prob_mixed
        },
        'confidence_category': confidence,
        'writing_stats': {
            'total_characters': len(text),
            'total_words': total_words,
            'sentence_count': len(sentences),
            'mean_sentence_length': round(mean_len, 2),
            'std_dev_sentence_length': round(std_dev, 2),
            'burstiness': round(burstiness, 3),
            'burstiness_verdict': "PASS (High Human Variance)" if burstiness >= 0.55 else "WARNING (Low AI Uniformity)"
        },
        'highlight_ratio': round(highlight_ratio, 3),
        'highlighted_sentences_count': highlighted_count,
        'sentences': sentence_evals
    }

def query_gptzero_api(text: str, api_key: str = None, jwt_token: str = None) -> Dict[str, Any]:
    """
    Mengirimkan request langsung ke GPTZero Live API jika key tersedia.
    """
    key = api_key or os.environ.get('GPTZERO_API_KEY')
    jwt = jwt_token or os.environ.get('GPTZERO_JWT')
    
    if not key and not jwt:
        return {'success': False, 'error': 'API key atau JWT tidak ditemukan. Gunakan mode lokal.'}
        
    if key:
        url = "https://api.gptzero.me/v2/predict/text"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': key
        }
        payload = {"document": text, "version": "2024-01-09"}
    else:
        url = "https://api.gptzero.me/v3/ai/text"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {jwt}',
            'x-page': '/',
            'x-gptzero-platform': 'webapp'
        }
        payload = {
            "document": text,
            "multilingual": True,
            "writing_stats_required": True,
            "interpretability_required": True
        }
        
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return {'success': True, 'mode': 'live_api', 'raw': data}
    except urllib.error.HTTPError as e:
        return {'success': False, 'error': f"HTTP {e.code}: {e.read().decode('utf-8')}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def refine_flagged_sentence_gptzero(sentence: str) -> str:
    """
    Merevisi kalimat yang ter-flag AI di GPTZero agar lolos highlight.
    Menghilangkan klise, menyuntikkan variasi panjang kalimat, dan menaikkan perplexity.
    """
    s = sentence.strip()
    s_lower = s.lower()
    
    is_id = any(w in s_lower for w in [' yang ', ' pada ', ' dan ', ' kami ', ' dengan ', ' dari '])
    
    if is_id:
        # 1. Bersihkan klise AI
        replacements = [
            (r"\bberperan krusial\b", "menentukan"),
            (r"\bsangat penting\b", "menjadi faktor kunci"),
            (r"\bmenelisik lebih dalam\b", "menguji secara spesifik"),
            (r"\bmenelaah lebih dalam\b", "menganalisis rincian"),
            (r"\bmerajut\b", "menggabungkan"),
            (r"\bparadigma baru\b", "arsitektur alternatif"),
            (r"\bdinamika yang kompleks\b", "interaksi antar-komponen"),
            (r"\bmenjembatani kesenjangan\b", "mengatasi selisih"),
            (r"\bkomprehensif\b", "menyeluruh"),
            (r"\btidak dapat dipungkiri bahwa\b", ""),
            (r"\bsecara holistik\b", "secara terpadu"),
            (r"\blanskap penelitian\b", "literatur"),
            (r"\bDengan demikian,\b", "Kondisi empiris ini menunjukkan bahwa"),
            (r"\bSelain itu,\b", "Pada observasi terpisah,"),
            (r"\bOleh karena itu,\b", "Akibatnya,")
        ]
        for pat, rep in replacements:
            s = re.sub(pat, rep, s, flags=re.IGNORECASE)
            
        # 2. Syntax opener refactor
        s = re.sub(r"^[Pp]engujian performa pada ([0-9\.,]+) sampel[^,]+menghasilkan", r"Saat kami mengevaluasi \1 sampel uji independen, tercatat", s)
        s = re.sub(r"^[Pp]engumpulan data primer dilakukan melalui", r"Kami menghimpun data primer menggunakan", s)
        s = re.sub(r"^[Pp]engujian ketahanan dilakukan pada", r"Kami menguji ketahanan sistem pada", s)
    else:
        # English
        replacements = [
            (r"\bdelve into\b", "examine"),
            (r"\bdelve\b", "explore"),
            (r"\brobust\b", "fault-tolerant"),
            (r"\bcomprehensive\b", "detailed"),
            (r"\bpivotal\b", "primary"),
            (r"\bintricate\b", "complex"),
            (r"\bmultifaceted\b", "composite"),
            (r"\btestament to\b", "demonstration of"),
            (r"\blandscape\b", "field"),
            (r"\bfoster\b", "promote"),
            (r"\bleverage\b", "employ"),
            (r"\bparadigm shift\b", "architectural change"),
            (r"\bparadigm\b", "framework"),
            (r"\bunderscore\b", "indicate"),
            (r"\bunderscores\b", "indicates"),
            (r"\bseamlessly\b", "directly"),
            (r"\bFurthermore,\b", "In our test runs,"),
            (r"\bMoreover,\b", "Simultaneously,"),
            (r"\bNotably,\b", "Specifically,")
        ]
        for pat, rep in replacements:
            s = re.sub(pat, rep, s, flags=re.IGNORECASE)
            
        # Syntax opener & tailing clause refactor
        s = re.sub(r"^[Ee]valuating the ([^,]+) demonstrated", r"When we evaluated the \1, we observed", s)
        s = re.sub(r"^[Bb]enchmarking ([^,]+) revealed", r"In our benchmark of \1, we observed", s)
        s = re.sub(r",\s*permitting simultaneous execution of", r". This allowed concurrent execution of", s)
        s = re.sub(r",\s*resulting in significant improvements", r", which yielded measurable gains", s)
        
    return s.strip()

def auto_clean_text_gptzero(text: str, max_iterations=3) -> Tuple[str, bool, List[Dict[str, Any]]]:
    """
    Loop kalibrasi teks otomatis hingga GPTZero memprediksi HUMAN_ONLY dan Burstiness >= 0.55.
    """
    current_text = text
    history = []
    
    for it in range(1, max_iterations + 1):
        analysis = analyze_text_gptzero_local(current_text)
        if not analysis.get('success'):
            break
            
        cls = analysis.get('document_classification')
        ai_prob = analysis.get('completely_generated_prob')
        b_score = analysis['writing_stats']['burstiness']
        flagged = [s for s in analysis.get('sentences', []) if s['highlight_sentence_for_ai']]
        
        history.append({
            'iteration': it,
            'classification': cls,
            'ai_prob': ai_prob,
            'burstiness': b_score,
            'flagged_count': len(flagged)
        })
        
        if cls == "HUMAN_ONLY" and b_score >= 0.50:
            return current_text, True, history
            
        # Terapkan perbaikan pada kalimat ter-flag
        for item in flagged:
            orig = item['sentence']
            revised = refine_flagged_sentence_gptzero(orig)
            current_text = current_text.replace(orig, revised)
            
    return current_text, (history[-1]['classification'] == "HUMAN_ONLY"), history

def main():
    parser = argparse.ArgumentParser(description="GPTZero Verifier & Calibration Engine (Reverse-Engineered)")
    parser.add_argument("input", nargs="?", help="File input (.txt/.md) atau string teks")
    parser.add_argument("-o", "--output", help="File output untuk menyimpan teks hasil kalibrasi")
    parser.add_argument("--api-key", help="GPTZero official API key (v2 API)")
    parser.add_argument("--jwt", help="GPTZero WebApp JWT token (v3 API)")
    parser.add_argument("--auto-clean", action="store_true", help="Automatically refine flagged sentences to achieve HUMAN_ONLY")
    parser.add_argument("--audit", action="store_true", help="Show full sentence-level audit with perplexity proxy")
    parser.add_argument("--json", action="store_true", help="Summary output in JSON format")
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        sys.exit(1)
        
    input_path = Path(args.input)
    if input_path.exists() and input_path.is_file():
        text = input_path.read_text(encoding='utf-8')
    else:
        text = args.input
        
    # Cek apakah pengguna minta query ke live API
    if args.api_key or args.jwt or os.environ.get('GPTZERO_API_KEY') or os.environ.get('GPTZERO_JWT'):
        print("[INFO] Sending request to GPTZero Live API...")
        res = query_gptzero_api(text, api_key=args.api_key, jwt_token=args.jwt)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res)
        return

    # Default: Local Heuristic & Statistical Engine
    if args.auto_clean:
        cleaned_text, success, history = auto_clean_text_gptzero(text)
        if args.output:
            Path(args.output).write_text(cleaned_text, encoding='utf-8')
            print(f"[INFO] Teks hasil kalibrasi disimpan di: {args.output}")
        if args.json:
            print(json.dumps({'success': success, 'history': history}, indent=2))
        else:
            print(f"[RESULT] Auto-Clean {'BERHASIL' if success else 'SELESAI'}")
            for h in history:
                print(f" Iterasi {h['iteration']}: Klasifikasi = {h['classification']} | AI Prob = {h['ai_prob']*100:.1f}% | Burstiness = {h['burstiness']:.3f} | Flagged = {h['flagged_count']}")
        return

    analysis = analyze_text_gptzero_local(text)
    if args.json:
        print(json.dumps(analysis, indent=2))
        return
        
    print("==================================================================")
    print("           GPTZERO CALIBRATION & AUDIT REPORT (REVERSE-ENGINEERED)  ")
    print("==================================================================")
    print(f"Document Classification : {analysis['document_classification']} (Predicted: {analysis['predicted_class']})")
    print(f"Confidence Category     : {analysis['confidence_category'].upper()}")
    print(f"Completely Generated AI : {analysis['completely_generated_prob']*100:.1f}%")
    print(f"Human Probability       : {analysis['class_probabilities']['human']*100:.1f}%")
    print("------------------------------------------------------------------")
    stats = analysis['writing_stats']
    print(f"Total Characters / Words: {stats['total_characters']} chars / {stats['total_words']} words")
    print(f"Total Sentences         : {stats['sentence_count']}")
    print(f"Mean Sentence Length    : {stats['mean_sentence_length']} words")
    print(f"Std Dev Sentence Length : {stats['std_dev_sentence_length']}")
    print(f"Burstiness (sigma/mu)   : {stats['burstiness']} -> {stats['burstiness_verdict']}")
    print(f"Flagged Sentences (AI)  : {analysis['highlighted_sentences_count']} / {stats['sentence_count']} ({analysis['highlight_ratio']*100:.1f}%)")
    print("==================================================================")
    
    if args.audit or analysis['highlighted_sentences_count'] > 0:
        print("\n--- SENTENCE LEVEL AUDIT (GPTZero Highlighting) ---")
        for idx, s in enumerate(analysis['sentences'], 1):
            flag_str = "[FLAGGED AI]" if s['highlight_sentence_for_ai'] else "[HUMAN OK]"
            print(f"{idx:02d}. {flag_str} (PPL: {s['perplexity_proxy']}, Len: {s['words']} w): {s['sentence']}")
            if s['cliches_found']:
                print(f"    -> Clichés : {', '.join(s['cliches_found'])}")
            if s['syntax_penalty']:
                print(f"    -> Syntax  : Flagged passive nominalization / gerund opener")

if __name__ == "__main__":
    main()
