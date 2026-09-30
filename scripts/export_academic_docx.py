# /// script
# dependencies = [
#     "python-docx>=1.1.0",
# ]
# ///
"""
export_academic_docx.py
-----------------------
Engine generator dokumen Microsoft Word (.docx) berstandar karya ilmiah & skripsi
mengacu pada: Keputusan Rektor Universitas Indonesia Nomor 2143/SK/R/UI/2017
tentang Pedoman Teknis Penulisan Tugas Akhir Mahasiswa Universitas Indonesia:
- Ukuran Kertas: A4 (80 gr, 21.5 cm x 29.7 cm)
- Margin: Kiri 4.0 cm (termasuk jilid), Atas 3.0 cm, Kanan 3.0 cm, Bawah 3.0 cm
- Font: Times New Roman 12 pt, 100% Hitam Murni (#000000)
- Paragraf: Spasi 1.5, Rata Kanan-Kiri (Justified), Indentasi Baris Pertama 1.0 cm
- Spasi Before/After = 0 pt
- Heading 1 (BAB): Bold, KAPITAL, Rata Tengah (Center), Angka Arab (contoh: BAB 3 METODE PENELITIAN)
- Heading 2 (Subbab): Bold, Title Case, Rata Kiri, jarak 1 spasi ke materi
- Tabel Ilmiah (Gaya APA): Hanya 3 garis lajur horizontal, tanpa garis kolom vertikal
- Footer Wajib: "Universitas Indonesia" (Arial 10 pt Bold, Align Right)
- Istilah Asing: Italic otomatis
"""

import sys
import re
import argparse
from pathlib import Path
import docx
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

COLOR_BLACK = RGBColor(0, 0, 0)
FONT_FAMILY = "Times New Roman"

def setup_page_layout(doc: Document, preset: str = "ui"):
    """Menyetel ukuran A4 dan margin standar UI (4 - 3 - 3 - 3 cm) serta footer wajib."""
    section = doc.sections[0]
    section.page_width = Cm(21.5)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(4.0)
    
    if preset == "ui":
        section.top_margin = Cm(3.0)
        section.right_margin = Cm(3.0)
        section.bottom_margin = Cm(3.0)
        
        # Tambahkan auto text footer "Universitas Indonesia" (Arial 10 pt Bold Align Right)
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = footer_p.add_run("Universitas Indonesia")
        run.font.name = "Arial"
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = COLOR_BLACK
    else:
        section.top_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        
    section.different_first_page_header_footer = False

def set_apa_table_borders(table):
    """Format tabel 3 garis horizontal gaya APA/ilmiah (tanpa garis kolom vertikal)."""
    tblPr = table._tbl.tblPr
    for child in list(tblPr):
        if child.tag.endswith("tblBorders"):
            tblPr.remove(child)

    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="none"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders_xml)

    if len(table.rows) > 0:
        for cell in table.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                f'<w:tcBorders {nsdecls("w")}>'
                f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
                f'</w:tcBorders>'
            )
            tcPr.append(tcBorders)

def add_runs_with_formatting(paragraph, text: str):
    """
    Memproses teks dengan format markdown inline:
    - *italic* / _italic_ -> font.italic = True
    - Strip bold di dalam teks tubuh agar mematuhi aturan anti-bold in-text.
    """
    # Bersihkan markdown bold (**text** -> text)
    cleaned_text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    
    # Parse italic (*text*)
    tokens = re.split(r"(\*[^*]+\*|_[^_]+_)", cleaned_text)
    for token in tokens:
        if not token:
            continue
        if (token.startswith("*") and token.endswith("*")) or (token.startswith("_") and token.endswith("_")):
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        else:
            run = paragraph.add_run(token)
            run.italic = False
        run.font.name = FONT_FAMILY
        run.font.size = Pt(12)
        run.font.color.rgb = COLOR_BLACK

def format_heading_1(doc: Document, text: str):
    """Judul BAB: TNR 12pt, Bold, KAPITAL, Center, 2 spasi."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(12)  # Jeda atas
    p.paragraph_format.space_after = Pt(24)   # Jarak 2 spasi (12pt * 2) ke subbab/isi
    p.paragraph_format.first_line_indent = Pt(0)
    
    run = p.add_run(text.upper())
    run.bold = True
    run.font.name = FONT_FAMILY
    run.font.size = Pt(12)
    run.font.color.rgb = COLOR_BLACK
    return p

def format_heading_2(doc: Document, text: str):
    """Judul Subbab: TNR 12pt, Bold, Title Case, Left, 1 spasi ke isi materi."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)  # Jarak 1 spasi (12pt) ke isi materi
    p.paragraph_format.first_line_indent = Pt(0)
    
    run = p.add_run(text)
    run.bold = True
    run.font.name = FONT_FAMILY
    run.font.size = Pt(12)
    run.font.color.rgb = COLOR_BLACK
    return p

def format_body_paragraph(doc: Document, text: str):
    """Isi Materi: TNR 12pt, Spasi 1.5, Justified, Indent 1.0 cm, Spacing Before/After 0."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.first_line_indent = Cm(1.0)
    
    add_runs_with_formatting(p, text)
    return p

def format_table_caption(doc: Document, text: str):
    """Judul Tabel: Rata kiri / tengah, Title Case, jarak 2 spasi dari teks sebelumnya."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(24)  # 2 spasi dari materi sebelumnya
    p.paragraph_format.space_after = Pt(6)    # Jeda ke fisik tabel
    p.paragraph_format.first_line_indent = Pt(0)
    
    run = p.add_run(text)
    run.bold = False
    run.font.name = FONT_FAMILY
    run.font.size = Pt(12)
    run.font.color.rgb = COLOR_BLACK
    return p

def format_figure_caption(doc: Document, text: str):
    """Judul Gambar: Rata tengah, ditaruh di bawah gambar, 2 spasi ke teks sesudahnya."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(24)   # 2 spasi ke teks berikutnya
    p.paragraph_format.first_line_indent = Pt(0)
    
    run = p.add_run(text)
    run.bold = False
    run.font.name = FONT_FAMILY
    run.font.size = Pt(12)
    run.font.color.rgb = COLOR_BLACK
    return p

def render_table_from_markdown(doc: Document, rows_data: list):
    """Membuat tabel docx berstandar APA 3 garis horizontal dari data baris markdown."""
    if not rows_data:
        return
    num_rows = len(rows_data)
    num_cols = len(rows_data[0])
    
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(table)
    
    for r_idx, row in enumerate(rows_data):
        for c_idx, cell_text in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.first_line_indent = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            run = p.add_run(cell_text.strip())
            run.font.name = FONT_FAMILY
            run.font.size = Pt(11 if num_cols > 4 else 12)
            run.font.color.rgb = COLOR_BLACK
            if r_idx == 0:
                run.bold = True
                
    # Berikan jeda setelah tabel ke teks berikutnya (2 spasi = 24pt)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(24)

def convert_markdown_to_academic_docx(md_content: str, output_path: str):
    """Membaca teks markdown dan mengonversinya ke file .docx berstandar akademik murni."""
    doc = Document()
    setup_page_layout(doc)
    
    lines = md_content.splitlines()
    in_table = False
    table_buffer = []
    
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        
        # Penanganan tabel markdown
        if line.startswith("|") and line.endswith("|"):
            # Periksa apakah garis pemisah header (|---|---|)
            if re.match(r"^\|[\s\-:|]+\|$", line):
                idx += 1
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            table_buffer.append(cells)
            in_table = True
            idx += 1
            continue
        else:
            if in_table and table_buffer:
                render_table_from_markdown(doc, table_buffer)
                table_buffer = []
                in_table = False

        if not line:
            idx += 1
            continue
            
        # Heading 1 (BAB)
        if line.startswith("# "):
            title = line[2:].strip()
            format_heading_1(doc, title)
        # Heading 2 (Subbab)
        elif line.startswith("## "):
            title = line[3:].strip()
            format_heading_2(doc, title)
        # Heading 3 (Anak Subbab)
        elif line.startswith("### "):
            title = line[4:].strip()
            p = format_heading_2(doc, title)
            # Make italic for level 3
            if p.runs:
                p.runs[0].italic = True
        # Judul Tabel
        elif line.lower().startswith("tabel ") and ("." in line or ":" in line):
            format_table_caption(doc, line)
        # Judul Gambar
        elif line.lower().startswith("gambar ") and ("." in line or ":" in line):
            format_figure_caption(doc, line)
        else:
            # Paragraf Isi Materi Normal
            format_body_paragraph(doc, line)
            
        idx += 1
        
    if in_table and table_buffer:
        render_table_from_markdown(doc, table_buffer)

    doc.save(output_path)
    print(f"[SUCCESS] Dokumen akademik berhasil dikompilasi: {output_path}")

def generate_sample_document(output_path: str):
    """Menghasilkan dokumen percontohan yang mematuhi seluruh aturan skripsi UI & anti-AI."""
    sample_md = """# BAB 3 METODE PENELITIAN

## 3.1. Desain Eksperimental dan Alur Kerja

Penelitian ini mengadopsi pendekatan kuasi-eksperimental dengan pengujian empiris berbasis komputasi terdistribusi. Rancangan sistem dievaluasi melalui tiga tahapan terstruktur yang meliputi pemrosesan awal data masukan, ekstraksi fitur menggunakan representasi vektor berdimensi tinggi, serta klasifikasi performa model. Seluruh tahapan eksperimen dijalankan secara berulang sebanyak 30 kali iterasi pengujian guna memperoleh estimasi selang kepercayaan (*confidence interval*) pada tingkat signifikansi 95 persen.

Pengujian performa inferensi dilakukan pada kluster komputasi lokal dengan spesifikasi perangkat keras unit pemroses grafis berkapasitas memori 16 gigabita. Kondisi latensi jaringan dipantau secara berkala selama transmisi data berlangsung untuk mengeliminasi potensi bias galat yang bersumber dari fluktuasi *throughput*.

## 3.2. Prosedur Sampling dan Penanganan Data

Populasi data primer bersumber dari repositori transaksi terdistribusi publik yang mencakup periode Januari 2024 hingga Desember 2025. Penentuan ukuran sampel minimum dihitung menggunakan formula Cochran dengan menetapkan batas toleransi galat sebesar lima persen dan proporsi variabilitas populasi sebesar 0.50. Berdasarkan perhitungan matematis tersebut, diperoleh ukuran sampel minimum sebanyak 384 entitas log transaksi.

Tabel 3.1 Distribusi Parameter Konfigurasi Pengujian Model

| Parameter Konfigurasi | Nilai Pengujian | Unit Pengukuran | Toleransi Ambang |
| Tingkat Pembelajaran (*Learning Rate*) | 0.0001 | Skalar | ± 0.00001 |
| Ukuran *Batch* (*Batch Size*) | 64 | Entitas Sampel | Konstan |
| Rasio Pembagian Data Latih dan Uji | 80 : 20 | Persentase | Eksak |
| Fungsi Optimasi Algoritma | AdamW | Bobot Adaptif | Peluruhan 0.01 |

Penanganan data yang hilang (*missing values*) diproses melalui metode imputasi berbasis tetangga terdekat (*k-nearest neighbors imputation*) dengan nilai k sama dengan lima. Entitas pencilan (*outliers*) yang memiliki deviasi absolut melebihi ambang batas tiga standar deviasi langsung dieksklusi dari himpunan data latih guna menjaga stabilitas kurva konvergensi.
"""
    convert_markdown_to_academic_docx(sample_md, output_path)

def main():
    parser = argparse.ArgumentParser(description="Academic Writing Engine DOCX Generator")
    parser.add_argument("input", nargs="?", help="File input markdown")
    parser.add_argument("output", nargs="?", help="File output .docx")
    parser.add_argument("--test", action="store_true", help="Generate sampel dokumen uji coba")
    
    args = parser.parse_args()
    
    if args.test:
        out_file = args.output or "sample_akademik.docx"
        generate_sample_document(out_file)
        sys.exit(0)
        
    if not args.input or not args.output:
        parser.print_help()
        sys.exit(1)
        
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] File input tidak ditemukan: {input_path}")
        sys.exit(1)
        
    md_content = input_path.read_text(encoding="utf-8")
    convert_markdown_to_academic_docx(md_content, args.output)

if __name__ == "__main__":
    main()
