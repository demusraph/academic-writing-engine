"""
verify_zerogpt.py
-----------------
Engine verifikasi dan kalibrasi otomatis langsung ke live API ZeroGPT
(https://api.zerogpt.com/api/detect/detectText).

Fitur:
- Memeriksa skor AI real-time, persentase fakePercentage, dan kalimat yang ter-flag (h).
- Mode Auto-Clean (--auto-clean): Otomatis membedah dan merevisi kalimat yang ter-flag
  menggunakan heuristik Academic Anti-AI hingga mencapai target skor 0.0% AI.
- Dukungan input file (.md, .txt) maupun string langsung.
- Standar pustaka Python murni (tanpa dependensi eksternal).
"""

import sys
import json
import time
import re
import argparse
import urllib.request
import urllib.error
from pathlib import Path

URL = 'https://api.zerogpt.com/api/detect/detectText'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'https://www.zerogpt.com',
    'Referer': 'https://www.zerogpt.com/',
    'Accept': 'application/json, text/plain, */*'
}

def query_zerogpt_api(text: str, max_retries=3):
    """Mengirimkan teks ke ZeroGPT live API dan mengembalikan hasil analisis."""
    clean_text = text.strip()
    if len(clean_text) == 0:
        return {'success': False, 'error': 'Teks kosong'}
        
    payload = {'input_text': clean_text}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode('utf-8'), headers=HEADERS, method='POST')
    
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('success') and 'data' in data:
                    d = data['data']
                    return {
                        'success': True,
                        'fakePercentage': float(d.get('fakePercentage', 0.0)),
                        'feedback': d.get('feedback', ''),
                        'aiWords': int(d.get('aiWords', 0)),
                        'textWords': int(d.get('textWords', 0)),
                        'flagged': d.get('h', []) or d.get('sentences', []),
                        'detected_language': d.get('detected_language', 'unknown')
                    }
                else:
                    return {'success': False, 'error': data.get('message', 'Format respons tidak valid')}
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5.0)
            else:
                time.sleep(2.0)
        except Exception as e:
            time.sleep(2.0)
            if attempt == max_retries - 1:
                return {'success': False, 'error': str(e)}
                
    return {'success': False, 'error': 'Maksimal percobaan gagal'}

def refine_flagged_sentence(sentence: str, lang: str = 'id') -> str:
    """Menerapkan transformasi anti-AI pada kalimat spesifik yang ter-flag."""
    s = sentence.strip()
    
    # Deteksi bahasa jika tidak ditentukan
    if lang == 'id' or any(w in s.lower() for w in ['yang', 'pada', 'dan', 'di', 'kami', 'dengan', 'dari']):
        # 1. Hapus pembuka nominalisasi pasif
        s = re.sub(r"^[Pp]engujian performa pada ([0-9\.,]+) sampel[^,]+menghasilkan", r"Saat kami mengevaluasi \1 sampel uji independen, tercatat", s)
        s = re.sub(r"^[Pp]engumpulan data primer dilakukan melalui", r"Kami menghimpun data primer menggunakan", s)
        s = re.sub(r"^[Pp]engujian ketahanan dilakukan pada", r"Kami menguji ketahanan sistem pada", s)
        s = re.sub(r"^[Ee]valuasi model[^,]+menunjukkan", r"Saat model dievaluasi, tercatat", s)
        
        # 2. Hapus konjungsi transisi simetris
        s = s.replace("Dengan demikian,", "Kondisi tersebut membuktikan bahwa")
        s = s.replace("Selain itu,", "Di samping itu,")
        s = s.replace("Oleh karena itu,", "Hal ini menyebabkan")
        
        # 3. Ubah klausa pasif panjang
        s = s.replace("dilakukan melalui", "kami jalankan menggunakan")
        s = s.replace("dilakukan menggunakan", "kami proses memakai")
        s = s.replace(", membuktikan bahwa", ". Temuan ini mengonfirmasi bahwa")
        s = s.replace("sehingga mekanisme", "yang mengakibatkan mekanisme")
    else:
        # Bahasa Inggris
        # 1. Hapus Gerund Opener
        s = re.sub(r"^[Ee]valuating the ([^,]+) demonstrated", r"When we evaluated the \1, we observed", s)
        s = re.sub(r"^[Bb]enchmarking ([^,]+) revealed", r"In our benchmark of \1, we observed", s)
        s = re.sub(r"^[Dd]ecoupling the ([^,]+) eliminated", r"We decoupled the \1 to resolve", s)
        
        # 2. Hapus Participial Tailing Modifiers
        s = re.sub(r", permitting simultaneous execution of", r". This allowed concurrent execution of", s)
        s = re.sub(r", triggering an unhandled segmentation fault", r". The process crashed with a segmentation fault", s)
        s = re.sub(r", causing write latencies to climb", r". As a result, write latencies climbed", s)
        s = re.sub(r", resulting in significant improvements", r", which yielded measurable improvements", s)
        
        # 3. Ganti transisi klise
        s = s.replace("Furthermore,", "In our tests,")
        s = s.replace("Moreover,", "At the same time,")
        s = s.replace("Notably,", "Specifically,")
        
    return s

def auto_clean_text(text: str, target_score=0.0, max_iterations=3):
    """Loop kalibrasi otomatis hingga teks mencapai target skor 0.0% AI."""
    current_text = text
    history = []
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n[ITERASI {iteration}] Menghubungi API ZeroGPT...")
        res = query_zerogpt_api(current_text)
        
        if not res.get('success'):
            print(f" [ERROR] Gagal memverifikasi: {res.get('error')}")
            break
            
        score = res.get('fakePercentage', 100.0)
        feedback = res.get('feedback', '')
        flagged = res.get('flagged', [])
        words = res.get('textWords', 0)
        lang = res.get('detected_language', 'id')
        
        history.append({
            'iteration': iteration,
            'score': score,
            'flagged_count': len(flagged)
        })
        
        print(f" -> Skor AI Saat Ini: {score}% | {feedback} | Total Kata: {words}")
        print(f" -> Jumlah Flagged Sentences: {len(flagged)}")
        
        if score <= target_score:
            print(f"\n[SUCCESS] Target skor tercapai ({score}% <= {target_score}%)!")
            return current_text, True, history
            
        print(" -> Menerapkan perbaikan heuristik Academic Anti-AI pada kalimat ter-flag:")
        for idx, f_sent in enumerate(flagged, 1):
            refined = refine_flagged_sentence(f_sent, lang)
            print(f"   [{idx}] Asli  : {f_sent[:80]}...")
            print(f"       Revisi: {refined[:80]}...")
            current_text = current_text.replace(f_sent.strip(), refined.strip())
            
        time.sleep(1.2)  # Delay antar-iterasi
        
    return current_text, False, history

def main():
    parser = argparse.ArgumentParser(description="ZeroGPT Live Verifier & Auto-Cleaner")
    parser.add_argument("input", nargs="?", help="File input (.txt/.md) atau string teks")
    parser.add_argument("-o", "--output", help="File output untuk menyimpan teks bersih")
    parser.add_argument("--auto-clean", action="store_true", help="Automatically refine flagged sentences until reaching 0.0%% AI")
    parser.add_argument("--target", type=float, default=0.0, help="Target maximum AI score (default: 0.0)")
    parser.add_argument("--json", action="store_true", help="Summary output in JSON format")
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        sys.exit(1)
        
    # Baca input teks
    input_path = Path(args.input)
    if input_path.exists() and input_path.is_file():
        content = input_path.read_text(encoding='utf-8')
    else:
        content = args.input
        
    if args.auto_clean:
        cleaned_text, success, history = auto_clean_text(content, target_score=args.target)
        if args.output:
            Path(args.output).write_text(cleaned_text, encoding='utf-8')
            print(f"\n[INFO] Teks hasil kalibrasi disimpan di: {args.output}")
        if args.json:
            print(json.dumps({'success': success, 'history': history}, indent=2))
    else:
        print("[INFO] Checking text against live ZeroGPT API...")
        res = query_zerogpt_api(content)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res.get('success'):
                print(f"Status: SUCCESS")
                print(f"AI Score: {res.get('fakePercentage')}%")
                print(f"Feedback: {res.get('feedback')}")
                print(f"AI Words Detected: {res.get('aiWords')} / {res.get('textWords')}")
                print(f"Flagged Sentences ({len(res.get('flagged', []))}):")
                for s in res.get('flagged', []):
                    print(f" - {s}")
            else:
                print(f"Error: {res.get('error')}")

if __name__ == "__main__":
    main()
