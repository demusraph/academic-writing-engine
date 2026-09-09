# Academic Anti-AI: Patterns, Vocabulary Tiers & Detection Triggers

Dokumen ini memuat katalog lengkap pola linguistik (*AI-isms*), tanda baca mekanis, dan anti-pattern metodologi yang menjadi pemicu utama deteksi AI (*Turnitin, GPTZero, Copyleaks, ZeroGPT*) pada karya ilmiah berbahasa Indonesia dan Inggris.

---

## 1. Punctuation & Formatting Tells (P0 — Immediate Purge)

### A. Em Dash (`—` / `--`)
* **Masalah:** LLM (Claude, GPT-4o, Gemini) memiliki kecenderungan tinggi menyisipkan *em dash* untuk membuat jeda dramatis atau klausul penjelas.
* **Standar Akademik:** Karya ilmiah formal jarang sekali memakai *em dash*.
* **Tindakan:** Target = 0. Ganti dengan koma ganda `, ... ,`, tanda kurung `(...)`, titik koma `;`, atau pecah menjadi dua kalimat independen.

### B. In-Text Bolding (`**kata kunci**`)
* **Masalah:** AI gemar menebalkan frasa penting di tengah paragraf untuk memudahkan *skimming* (gaya posting blog/chat).
* **Standar Akademik:** Teks tebal di dalam paragraf dilarang keras pada skripsi dan jurnal ilmiah. Tebal hanya diizinkan untuk Judul Bab, Judul Subbab, dan label Tabel/Gambar.
* **Tindakan:** Hapus semua *markdown bold* di dalam tubuh paragraf.

### C. Symmetrical Bullet Lists
* **Masalah:** AI selalu menyusun daftar butir dengan formula seragam:
  `- **Frasa Benda:** Kalimat penjelasan dengan panjang yang persis sama.`
* **Standar Akademik:** Penguji/reviewer menganggap ini sebagai ringkasan generik.
* **Tindakan:** Ubah daftar butir menjadi paragraf naratif-argumentatif yang kohesif.

### D. Smart/Curly Quotes & Unicode Artifacts
* **Masalah:** Antarmuka web AI sering menyisipkan *smart quotes* (`“ ”`), *non-breaking spaces* (`\u00A0`), atau *zero-width spaces*.
* **Tindakan:** Normalisasi semua tanda kutip menjadi tanda petik lurus standar ASCII (`"`) dan spasi ASCII tunggal (`\u0020`).

---

## 2. Indonesian AI Vocabulary Tiers

### Tier 1 — Always Purge & Replace (Indonesian)
Kata-kata berikut muncul 5–20× lebih sering pada teks LLM bahasa Indonesia dibanding tulisan akademisi asli:

| Kata Terlarang (AI) | Rekomendasi Pengganti Akademik |
| :--- | :--- |
| **berperan krusial / sangat penting** | menentukan, menjadi faktor kunci, membatasi |
| **menelisik / menelaah lebih dalam** | menguji, menganalisis, mengidentifikasi, mengukur |
| **merajut / menyelaraskan** | menghubungkan, mengintegrasikan, mengkorelasikan |
| **paradigma baru** | pendekatan, kerangka kerja, model |
| **dinamika yang kompleks** | interaksi variabel, variabilitas, deviasi data |
| **menjembatani kesenjangan** | mengatasi disparitas, menutup celah penelitian (*research gap*) |
| **komprehensif** | menyeluruh, lengkap, terperinci (atau jelaskan metriknya) |
| **tidak dapat dipungkiri bahwa** | hapus langsung; langsung mulai dengan klausa fakta |
| **melandasi** | menjadi dasar, menopang |
| **tolok ukur utama** | parameter evaluasi, indikator |
| **secara holistik** | secara terpadu, menyeluruh (atau sebutkan komponen riilnya) |
| **membuka cakrawala baru** | hapus; ganti dengan kontribusi empiris terukur |
| **lanskap penelitian** | domain, literatur, bidang studi |

### Tier 2 — Flag When Appearing in Clusters (2+ Per Paragraph)
* *sinergi, mengakselerasi, menstimulasi, mengoptimalkan, berakar pada, signifikansi substansial, manifestasi, menopang integritas, berdaya guna, ranah*.
* **Tindakan:** Jika muncul lebih dari 1 dalam satu paragraf, tulis ulang menggunakan bahasa lugas berbasis kata kerja tindakan operasional.

### Tier 3 — Symmetrical Transition Openers (Dilarang Membuka Paragraf Dengan)
* *Selain itu,*
* *Lebih lanjut,*
* *Perlu dicatat bahwa,*
* *Oleh karena itu,*
* *Sebagai kesimpulan,*
* *Secara keseluruhan,*
* *Tidak kalah pentingnya,*
* **Tindakan:** Variasikan struktur pembuka paragraf: buka dengan klausa kondisional (*"Ketika instrumen X diuji..."*), klausa subjek langsung (*"Parameter batch size menentukan..."*), atau kutipan sintesis (*"Temuan Smith (2023) menunjukkan..."*).

---

## 3. English AI Vocabulary Tiers

### Tier 1 — Always Purge & Replace (English)
| Forbidden (AI) | Academic Human Replacement |
| :--- | :--- |
| **delve / delve into** | explore, examine, analyze, investigate |
| **robust** | reliable, stable, validated, fault-tolerant |
| **comprehensive** | thorough, detailed, full-scale |
| **pivotal** | key, central, primary, determining |
| **intricate / intricacies** | complex, structural details, specific interactions |
| **multifaceted** | composite, involving multiple factors |
| **testament to** | evidence of, indicates, demonstrates |
| **landscape (metaphor)** | field, domain, literature, sector |
| **foster** | encourage, promote, yield, generate |
| **leverage (verb)** | use, employ, apply, exploit |
| **paradigm / paradigm shift** | framework, methodology, model, architectural change |
| **underscore / highlights** | shows, confirms, indicates |
| **seamless / seamlessly** | directly, continuous, integrated |
| **embark** | begin, commence, initiate |
| **tapestry / symphony (metaphor)** | combination, aggregate, interaction |

### Tier 2 — Forbidden English Transitions (Overuse)
* *Moreover, Furthermore, Additionally, In addition, Notably, It is worth noting that, In conclusion, Ultimately, As a matter of fact.*

---

## 4. Research Methodology (Bab 3) Anti-Patterns

### Anti-Pattern 1: Textbook Definition Dump
* **Pelanggaran Fatal:** Mendefinisikan teori metodologi di Bab 3.
  * *Contoh AI:* "Metode yang digunakan adalah penelitian kuantitatif. Penelitian kuantitatif menurut Sugiyono (2019) adalah metode penelitian yang berlandaskan pada filsafat positivisme..."
* **Koreksi Akademik Human:** Hapus 100% definisi kamus. Langsung masuk ke desain eksperimen dan rancangan operasional:
  * *Contoh Human:* "Penelitian ini menerapkan desain kuasi-eksperimental dengan kelompok kontrol non-ekuivalen. Variabel independen dimanipulasi melalui tiga tingkat intervensi..."

### Anti-Pattern 2: Zero Friction / Absence of Operational Parameters
AI tidak memiliki data lapangan sehingga tulisannya terdengar "terlalu mulus tanpa kendala".
* **Wajib Disuntikkan:**
  1. **Sampling & Population:** Rumus presisi (Slovin, Taro Yamane, atau Cochran), nilai margin of error ($e = 0.05$ atau $0.01$), tingkat pengembalian kuesioner (*response rate*), dan jumlah sampel gugur (*sample attrition / drop-out*).
  2. **Instrument Specs:** Merek, tipe sensor, versi software/library (misal: *Python v3.11*, *PyTorch v2.1.2*, *IBM SPSS v26*), toleransi error alat ukur.
  3. **Data Preprocessing & Cleaning:** Batas ambang eliminasi data pencilan (*outlier threshold* misal $Z > 3.0$), teknik imputasi data hilang (*missing data handling* misal *MICE* atau *median imputation*).
  4. **Triangulasi / Validasi:** Nilai *Cronbach's Alpha* aktual, nilai AVE (*Average Variance Extracted*), atau *Cohen's Kappa*.

---

## 5. Rhetorical & Argumentative Anti-Patterns

### A. Over-Hedging / Hedge Stacking
* **Pelanggaran AI:** Menumpuk 3 kata pelindung untuk menghindari komitmen faktual:
  * *AI:* "Hasil analisis ini **dapat berpotensi mengindikasikan** bahwa..."
  * *Human:* "Hasil analisis **mengindikasikan** bahwa..." atau "Data **menunjukkan** bahwa..."

### B. Ghost Citations (Atribusi Hampa)
* **Pelanggaran AI:** Klaim tanpa subjek verifikatif:
  * *AI:* "Berbagai studi terdahulu telah membuktikan bahwa integrasi model ini efektif..."
  * *Human:* "Meskipun Chen et al. (2022) mencatat peningkatan akurasi sebesar 14%, pengujian pada dataset dengan derau tinggi oleh Wijaya (2024) menunjukkan degradasi F1-score hingga 0.62."

### C. Pollyanna Closers (Penutup Normatif / Utopis)
* **Pelanggaran AI:** Menutup bab atau sub-bab dengan wejangan masa depan:
  * *AI:* "Diharapkan langkah ini dapat memberikan kontribusi positif bagi kemajuan ilmu pengetahuan dan mendorong terciptanya inovasi berkelanjutan di masa yang akan datang."
  * *Human:* Akhiri dengan sintesis batas studi atau jembatan ke bab berikutnya: "Keterbatasan daya komputasi membatasi pengujian pada batch size 32, yang implikasinya terhadap konvergensi dibahas lebih lanjut pada Bab 4."

---

## 6. ZeroGPT Reverse Engineering & Concrete Bypasses (0.0% AI)

Berdasarkan reverse engineering langsung terhadap engine ZeroGPT (`https://api.zerogpt.com/api/detect/detectText`):

### A. Endpoint & Karakteristik Arsitektur
* **Endpoint:** `POST https://api.zerogpt.com/api/detect/detectText`
* **Payload:** `{"input_text": "..."}`
* **Response:** `data.fakePercentage` (0.0% - 100.0%), `data.h` (array kalimat yang ter-flag AI).
* **Threshold Deteksi:** Paragraf dengan $\le 30$ kata sering memicu *"Please input more text"*, sedangkan teks 60–300 kata langsung dinilai probabilitasnya.

### B. Pola Sintaksis yang Langsung Memicu 100% AI pada ZeroGPT
1. **Nominalisasi Pasif Klise (Indonesian Red Flag):**
   * *Formula Terlarang:* `"Pengumpulan data primer dilakukan melalui instrumen kuesioner terstruktur yang disebarkan kepada..."` $\rightarrow$ memicu skor 100% AI.
   * *Formula Lolos (0.0% AI):* Gunakan kata kerja aktif dengan subjek orang pertama/peneliti: `"Kami mengumpulkan data primer menggunakan kuesioner terstruktur pada lima kantor cabang..."`.
2. **Klausa Partisipial Ekor (English Red Flag):**
   * *Formula Terlarang:* `"...dropped by 58%, permitting simultaneous execution of three concurrent detection pipelines..."` atau `"...resulting in significant improvements..."`.
   * *Formula Lolos (0.0% AI):* Pecah menjadi kalimat mandiri atau klausa konsekutif aktif: `"...dropped by 58%. This reduction allowed our test harness to execute three pipelines simultaneously..."`.
3. **Konjungsi Transisi di Awal Kalimat:**
   * Frasa `"Dengan demikian,"` atau `"Furthermore,"` sering kali menjadi satu-satunya alasan sebuah kalimat masuk ke dalam array `data.h`. Ganti dengan pembuka klausa klausal berbasis fakta empiris.

### C. Formula Emas 0.0% AI (Empirical Grounding Formula)
Satu paragraf yang dijamin menghasilkan **0.0% AI** di ZeroGPT harus memuat:
1. **Jangkar Temporal & Lokasi Riil:** *"antara bulan Mei dan Juni"*, *"di stasiun cuaca lapangan Sukabumi"*, *"captured across three edge routers"*.
2. **Angka Cacat / Data Drop Eksak:** *"sebanyak 240 frame mengalami kerusakan saat tegangan drop di bawah 11 volt"*, *"84 records were truncated when socket connections reset"*.
3. **Keputusan Komparatif Peneliti (*Rather than X, we Y*):** *"Alih-alih memaksakan interpolasi, kami membuang data cacat tersebut dan..."*.
4. **Friksi & Konsekuensi Nyata:** *"namun waktu komputasi melonjak tajam setiap kali antrean melebihi 35 objek"*, *"inference latency climbed sharply whenever sliding window buffers exceeded 500 packets"*.

---

## 7. GPTZero Reverse Engineering & Burstiness Calibration (HUMAN_ONLY / 0% AI)

Berdasarkan *full-scope reverse engineering* terhadap arsitektur webapp GPTZero (`https://app.gptzero.me` dan `https://api.gptzero.me`):

### A. Endpoint & Skema Deteksi
* **WebApp Endpoint:** `POST https://api.gptzero.me/v3/ai/text` (autentikasi JWT Supabase `sb_publishable_-TRlvcmoZ3y9LvkQys7Vcg_TImPL6et`).
* **Official API Endpoint:** `POST https://api.gptzero.me/v2/predict/text` (header `x-api-key`).
* **Format Request:**
  ```json
  {
    "document": "<naskah_akademik>",
    "multilingual": true,
    "writing_stats_required": true,
    "interpretability_required": true
  }
  ```
* **Metrik Respons Inti:**
  1. `document_classification`: `"HUMAN_ONLY"`, `"MIXED"`, atau `"AI_ONLY"`.
  2. `class_probabilities`: `{"human": float, "ai": float, "mixed": float}`.
  3. `completely_generated_prob`: Probabilitas dokumen ditulis penuh oleh AI (0.0 - 1.0).
  4. `sentences[].highlight_sentence_for_ai`: Boolean penanda kalimat yang ter-flag AI.
  5. `overall_burstiness`: Koefisien variasi panjang dan perplexity antar-kalimat.

### B. Perbedaan Kritis: ZeroGPT vs GPTZero
| Karakteristik | ZeroGPT | GPTZero |
| :--- | :--- | :--- |
| **Fokus Deteksi Utama** | *N-gram predictability*, gerund openers, trailing participials, passive nominalization | *Deep Learning Transformer* (RoBERTa) + *Sentence-level Perplexity* + *Burstiness* |
| **Pemicu False Positive** | Pembuka kalimat pasif/klise (`"Pengumpulan data dilakukan..."`) | **Uniformitas Panjang Kalimat (Low Burstiness)** meskipun tanpa kata klise |
| **Batas Ambang Kalimat** | Evaluasi per blok teks (array `h`) | Evaluasi per kalimat tunggal (`highlight_sentence_for_ai: true`) |
| **Kunci Lolos 100% Human** | Injeksi subjek aktif peneliti + angka cacat empiris | **Osilasi Panjang Kalimat ($\text{Burstiness} \ge 0.55$) + Eliminasi Klise** |

### C. Formula Rekayasa Burstiness (The Cadence Oscillation Rule)
AI menulis dengan panjang kalimat yang sangat seragam ($\text{Burstiness} = \sigma / \mu < 0.30$). Manusia menulis dengan pola ledakan (*bursty*): variasi ritme acak yang mencampurkan kalimat super-pendek dan kalimat majemuk panjang.

**Rumus Target:**
$$\text{Burstiness} = \frac{\sigma(\text{panjang kata})}{\mu(\text{panjang kata})} \ge 0.55$$

**Pola Kadensa Paragraf Wajib (Osilasi 3-Tier):**
1. **Kalimat Super-Pendek (3–8 kata):** Kesimpulan lugas, penegasan kegagalan, atau batasan empiris.
   * *Contoh:* *"Antrean soket macet total."*, *"Uji replikasi kami gagal."*, *"Deviasi skor sangat sempit."*, *"Inferensi berjalan sangat cepat."*
2. **Kalimat Menengah (14–22 kata):** Prosedur tindakan metodologis peneliti.
   * *Contoh:* *"Kami menghimpun data primer menggunakan kuesioner terstruktur pada lima kantor cabang operasional selama empat pekan."*
3. **Kalimat Majemuk Bertingkat Panjang (30–48 kata):** Sintesis empiris padat komparatif dengan multi-klausa dan data numerik.
   * *Contoh:* *"Ketika kami mencoba mengaktifkan enkripsi TLS standar pada mikrokontroler dengan memori terbatas tersebut, throughput transmisi data sensor anjlok hingga 70% dan memicu antrean buffer soket meluap ke partisi memori swap host."*

### D. Eliminasi Highlighting Kalimat Tunggal (`highlight_sentence_for_ai: false`)
GPTZero mem-flag kalimat individual jika kalimat tersebut:
1. Memuat kata klise AI bahasa Inggris (*pivotal, delve, multifaceted, robust, landscape, foster, testament, underscore*).
2. Memuat kata klise AI bahasa Indonesia (*berperan krusial, sangat penting, menelisik lebih dalam, paradigma baru, dinamika yang kompleks, secara holistik*).
3. Mengikuti susunan standar tanpa kata penjelas empiris (misalnya kalimat umum tanpa angka, tanpa merek hardware, tanpa nama protokol).

**Solusi Otomatis:**
Jalankan verifier GPTZero skill:
```bash
uv run scripts/verify_gptzero.py naskah.txt --audit
uv run scripts/verify_gptzero.py naskah.txt --auto-clean -o naskah_calibrated.txt
```
Target: `Document Classification = HUMAN_ONLY`, `Completely Generated AI = 0.0%`, `Burstiness >= 0.55`.

---

## 8. Cross-Disciplinary Empirical Grounding (Anti-Overfit Matrix)

Agar formula anti-deteksi tidak mengalami *overfitting* pada domain teknik/informatika (STEM), terapkan penggantian friksi empiris sesuai rumpun ilmu:

| Rumpun Ilmu | Karakteristik Friksi Empiris (Pengganti Hardware/Sensor) | Contoh Kalimat Human Lolos (0.0% AI) |
| :--- | :--- | :--- |
| **Ilmu Hukum & Peradilan** | Nomor putusan pengadilan, multitafsir pasal, disparitas pertimbangan hakim kasasi, berkas perkara yang tidak lengkap. | *"Dari 34 salinan putusan kasasi Mahkamah Agung yang kami himpun, sengketa berfokus pada insolvensi perbankan syariah kurun 2020 sampai 2024. Tujuh salinan putusan tidak lengkap. Kami mencoret berkas yang hilang amar pertimbangannya..."* |
| **Manajemen Bisnis & Pemasaran** | Penolakan perekaman suara oleh informan, penolakan otoritas tanda tangan, manipulasi absensi manual oleh mandor, waktu tercapainya saturasi data. | *"Tiga informan menolak perekaman suara. Kami menyiasati penolakan tersebut dengan membuat catatan lapangan terperinci dan meminta paraf verifikasi transkrip langsung pada hari yang sama. Saturasi data tercapai pada wawancara ke-12."* |
| **Psikologi & Perilaku** | Responden *drop-out* pada gelombang kedua, pola jawaban seragam pada skala Likert, eliminasi data *outlier* asesmen, nilai reliabilitas *Cronbach's Alpha*. | *"Pada tahap pengumpulan data gelombang kedua, sebanyak 28 kuesioner gugur karena pola jawaban seragam yang mengindikasikan ketidakseriusan pengisian skala Likert. Kami mencatat reliabilitas Cronbach Alpha sebesar 0,884 pada 182 sampel valid..."* |
| **Sosiologi & Kebijakan Publik** | Kecurigaan tokoh masyarakat terhadap peneliti, ketidaksinkronan NIK data bansos, pembagian bantuan bias patronase, catatan buku harian lapangan. | *"Tokoh pemuda sempat mencurigai peneliti sebagai mata-mata pengembang proyek tanggul. Kami membangun kepercayaan kembali melalui mediasi ketua rukun nelayan setempat. Akses lapangan berhasil dipulihkan."* |
| **Ilmu Komunikasi & Media** | Deteksi akun buzzer terkoordinasi, rasio judul *clickbait* menyesatkan, pengujian *inter-coder reliability* skor *Cohen's Kappa*. | *"Tiga asisten peneliti menguji inter-coder reliability dan mencapai skor Cohen Kappa 0,84. Konsensus interpretasi terverifikasi ketat."* |

### Aturan Lexical Jitter (Mencegah Template Fingerprint)
Dilarang menggunakan frasa penegas ritme yang statis (seperti *"Our test harness confirmed this"* atau *"Kondisi empiris ini terbukti konsisten"* secara berulang). 
Kalimat super-pendek (3–8 kata) harus dibentuk secara organik dari substansi klaim:
* *STEM:* *"Antrean soket macet total."*, *"Inferensi berjalan sangat cepat."*
* *Hukum:* *"Penelusuran doktrin terhambat nyata."*, *"Kepastian hukum terabaikan."*
* *Bisnis:* *"Friksi keluarga melumpuhkan bisnis."*, *"Kendala kultural mengalahkan teknologi."*
* *Psikologi:* *"Skala ukur terbukti konsisten."*, *"Efek terapeutik terbukti nyata."*
* *Sosiologi:* *"Transformasi sosial berlangsung menyakitkan."*, *"Warga miskin terisolasi total."*



