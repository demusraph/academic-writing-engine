# Academic Anti-AI: Linguistic Patterns, Vocabulary Tiers & Detection Triggers

Complete catalog of linguistic artifacts (*AI-isms*), mechanical punctuation tells, and methodology anti-patterns that trigger institutional AI classifiers (*Turnitin, GPTZero, Copyleaks, ZeroGPT, Originality.ai*).

---

## 1. Punctuation & Formatting Tells (P0 — Immediate Purge)

### A. Em Dash (`—` / `--`)
* **Problem:** Large Language Models (Claude, GPT-4o, Gemini) disproportionately insert *em dashes* to construct dramatic rhetorical pauses or parenthetical explanations.
* **Academic Standard:** Formal peer-reviewed literature and dissertations use commas, parentheses, or separate sentences.
* **Action:** Target = 0. Replace with double commas `, ... ,`, parentheses `(...)`, semicolons `;`, or split into two independent sentences.

### B. In-Text Bolding (`**key concept**`)
* **Problem:** AI models frequently bold mid-sentence concepts to facilitate skimming (blog/conversational style).
* **Academic Standard:** Bolding inside body paragraphs is strictly forbidden in academic manuscripts. Bold is reserved solely for Headings and Table labels.
* **Action:** Strip all markdown bold formatting inside paragraph bodies.

### C. Symmetrical Bullet Lists
* **Problem:** AI models reflexively format arguments into symmetrical bulleted lists:
  `- **Noun Phrase:** Explanatory sentence of identical length.`
* **Academic Standard:** Reviewers identify this as a generic AI summarization pattern.
* **Action:** Convert bullet points into cohesive argumentative narrative prose.

### D. Smart Quotes & Unicode Artifacts
* **Problem:** AI copy-paste operations often introduce smart quotes (`“ ”`), non-breaking spaces (`\u00A0`), or zero-width spaces.
* **Action:** Normalize all quotation marks to standard ASCII straight quotes (`"`) and standard spaces (`\u0020`).

---

## 2. English AI Vocabulary Tiers

### Tier 1 — Always Purge & Replace (English)
The following terms appear 5–20x more frequently in LLM outputs than in human academic writing:

| AI Cliché Term | Academic Alternative |
| :--- | :--- |
| **delve / delve into** | examine, investigate, explore, analyze |
| **robust** | fault-tolerant, resilient, verified, stable |
| **comprehensive** | thorough, detailed, exhaustive, systematic |
| **pivotal / crucial** | essential, primary, governing, determinant |
| **intricate / intricacies** | complex, fine-grained, detailed interactions |
| **multifaceted** | composite, heterogeneous, multi-variable |
| **testament to** | demonstration of, evidence of, indicates |
| **landscape** | domain, field, literature, discipline |
| **foster / nurture** | promote, facilitate, enable, cultivate |
| **leverage** | employ, utilize, apply, implement |
| **paradigm / paradigm shift** | framework, methodology, structural transition |
| **underscore / underscores** | highlights, demonstrates, reveals, shows |
| **seamless / seamlessly** | directly, integrated, without interruption |
| **game-changer** | substantial development, critical advance |
| **in conclusion / to summarize** | remove; begin directly with empirical findings |

---

## 3. Indonesian AI Vocabulary Tiers

### Tier 1 — Always Purge & Replace (Indonesian)
Words that appear overwhelmingly in machine-translated or LLM-generated Indonesian prose:

| Kata Terlarang (AI) | Rekomendasi Pengganti Akademik |
| :--- | :--- |
| **berperan krusial / sangat penting** | menentukan, menjadi faktor kunci, membatasi |
| **menelisik / menelaah lebih dalam** | menguji, menganalisis, mengidentifikasi, mengukur |
| **merajut / menyelaraskan** | menghubungkan, mengintegrasikan, mengkorelasikan |
| **paradigma baru** | pendekatan alternatif, kerangka kerja, model |
| **dinamika yang kompleks** | interaksi variabel, variabilitas, deviasi data |
| **menjembatani kesenjangan** | mengatasi disparitas, menutup celah penelitian (*research gap*) |
| **komprehensif** | menyeluruh, terperinci, sistematis |
| **tidak dapat dipungkiri bahwa** | hapus langsung; mulai dengan klausa fakta |
| **melandasi** | menjadi dasar, menopang |
| **tolok ukur utama** | parameter evaluasi, indikator performa |
| **secara holistik** | secara terpadu, menyeluruh |
| **membuka cakrawala baru** | hapus; gantikan dengan kontribusi empiris |
| **lanskap penelitian** | domain, literatur, bidang studi |

---

## 4. Forbidden Transition Openers (Never Open Paragraphs With)

* *Moreover, Furthermore, Additionally, In addition, It is worth noting that, Notably, Consequently, Ultimately.*
* *Selain itu, Lebih lanjut, Perlu dicatat bahwa, Oleh karena itu, Tidak dapat dipungkiri bahwa, Sebagai kesimpulan, Secara keseluruhan.*
