"""Compose a math worksheet from a version 1 source file."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree.ElementTree import Element, SubElement, ElementTree


def native_math(parts):
    from docx.oxml import OxmlElement

    def node(name, *children):
        result = OxmlElement("m:" + name)
        for child in children:
            result.append(child)
        return result

    def expression(parts):
        return node("e", *(part(value) for value in parts))

    def part(value):
        if isinstance(value, str):
            run_text = node("t")
            run_text.text = value
            return node("r", run_text)
        kind, cells = next(iter(value.items()))
        if kind in ("frac", "sup"):
            first, second = cells
            if kind == "frac":
                return node("f", node("num", part(first)), node("den", part(second)))
            return node("sSup", node("e", part(first)), node("sup", part(second)))
        if kind == "system":
            begin = node("begChr")
            end = node("endChr")
            from docx.oxml.ns import qn
            begin.set(qn("m:val"), "{")
            end.set(qn("m:val"), "")
            return node("d", node("dPr", begin, end),
                        node("e", node("eqArr", *(expression(row) for row in cells))))
        matrix = node("m", *(node("mr", *(expression([cell]) for cell in row)) for row in cells))
        return node("d", node("e", matrix))

    return node("oMath", *(part(value) for value in parts))


def validate_parts(parts):
    if not isinstance(parts, list) or not parts:
        raise ValueError("公式 parts 必須為非空陣列")
    for value in parts:
        if isinstance(value, str) and value:
            continue
        if not isinstance(value, dict) or len(value) != 1:
            raise ValueError("無效的公式結構")
        kind, rows = next(iter(value.items()))
        if kind in ("frac", "sup") and isinstance(rows, list) and len(rows) == 2:
            validate_parts(rows)
        elif kind in ("matrix", "system") and isinstance(rows, list) and rows:
            if kind == "matrix" and any(len(row) != len(rows[0]) for row in rows):
                raise ValueError("矩陣每列的欄數必須一致")
            for row in rows:
                validate_parts(row)
        else:
            raise ValueError(f"不支援的公式結構：{kind}")


def diagram(spec, svg_path=None, png_path=None):
    width, height = spec["size"]
    if not all(type(v) is int and 0 < v <= 2000 for v in (width, height)):
        raise ValueError("圖面尺寸須是 1–2000 的整數")
    svg = Element("svg", xmlns="http://www.w3.org/2000/svg", viewBox=f"0 0 {width} {height}")
    SubElement(svg, "title").text = spec["alt"]
    SubElement(svg, "rect", width=str(width), height=str(height), fill="white")
    if png_path:
        from PIL import Image, ImageDraw, ImageFont
        picture = Image.new("RGB", (3 * width, 3 * height), "white")
        canvas = ImageDraw.Draw(picture)
        font_path = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
        if not font_path.is_file() and shutil.which("fc-match"):
            font_path = Path(subprocess.check_output(
                ["fc-match", "-f", "%{file}", "DejaVu Sans"], text=True))
        font = ImageFont.truetype(str(font_path), 38) if font_path.is_file() else ImageFont.load_default(size=38)

    def draw_line(points, dashed=False):
        if len(points) < 2:
            raise ValueError("線至少需要兩點")
        if not all(math.isfinite(x) and math.isfinite(y) for x, y in points):
            raise ValueError("座標須為有限數值")
        element = SubElement(svg, "polyline", points=" ".join(f"{x:.3f},{y:.3f}" for x, y in points),
                             fill="none", stroke="#181818", **{"stroke-width": "2"})
        if dashed:
            element.set("stroke-dasharray", "6 5")
        if png_path:
            if not dashed:
                canvas.line([(3 * x, 3 * y) for x, y in points], fill="#181818", width=6)
                return
            distance = 0.0
            for start, end in zip(points, points[1:]):
                length = math.dist(start, end)
                offset = 0.0
                while offset < length:
                    phase = (distance + offset) % 11
                    ink = phase < 6
                    step = min(length - offset, max((6 if ink else 11) - phase, 1e-6))
                    if ink:
                        segment = [tuple(3 * (a + (b - a) * t / length) for a, b in zip(start, end))
                                   for t in (offset, offset + step)]
                        canvas.line(segment, fill="#181818", width=6)
                    offset += step
                distance += length

    for line in spec.get("lines", []):
        draw_line(line)
    for x, y, radius, start, sweep in spec.get("arcs", []):
        angles = [math.radians(start + sweep * index / 90) for index in range(91)]
        draw_line([(x + radius * math.cos(a), y - radius * math.sin(a)) for a in angles])
    for curve in spec.get("curves", []):
        function = {"sin": math.sin, "cos": math.cos, "reciprocal": lambda t: 1 / t}[curve["function"]]
        ox, oy = curve["origin"]
        sx, sy = curve["scale"]
        for low, high in curve["domains"]:
            if not low < high or (curve["function"] == "reciprocal" and low <= 0 <= high):
                raise ValueError("函數區間無效或跨越不連續點")
            values = [low + (high - low) * index / 300 for index in range(301)]
            draw_line([(ox + sx * t, oy - sy * function(t)) for t in values], curve.get("dashed", False))
    for x, y, label in spec.get("labels", []):
        SubElement(svg, "text", x=str(x), y=str(y), **{"font-size": "13", "font-family": "sans-serif"}).text = label
        if png_path:
            canvas.text((x * 3, y * 3), label, font=font, fill="black", anchor="ls")
    if svg_path:
        ElementTree(svg).write(svg_path, encoding="utf-8", xml_declaration=True)
    if png_path:
        picture.save(png_path)


def validate(source):
    required = ("title", "stage", "purpose")
    if source.get("version") != 1 or any(not source.get(key) for key in required):
        raise ValueError("缺少教材版本、標題、學段或用途")
    ids = set()
    for item in source["items"]:
        key = item["id"]
        if not key.isascii() or not key.isalnum() or key in ids or not item["prompt"]:
            raise ValueError("題目 ID 須是唯一英數字，且須有題幹")
        ids.add(key)
        if "formula" in item:
            if not item["formula"]["latex"]:
                raise ValueError("缺少 LaTeX 原文")
            validate_parts(item["formula"]["parts"])
        if "figure" in item:
            diagram(item["figure"])
        if "table" in item:
            rows = item["table"]
            if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
                raise ValueError("表格欄數不一致")
        if not 0 <= item.get("answer_lines", 0) <= 12:
            raise ValueError("作答行數須介於 0 到 12")
    if not ids:
        raise ValueError("教材至少須有一題")


def document(source, path, assets, teacher):
    from docx import Document
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(1.6)
    section.left_margin = section.right_margin = Cm(1.8)
    for name, size in (("Normal", 11), ("Title", 24), ("Heading 2", 13)):
        style = doc.styles[name]
        style.font.name = "Noto Sans TC"
        fonts = style.element.get_or_add_rPr().rFonts
        for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
            fonts.attrib.pop(qn("w:" + attr), None)
        fonts.set(qn("w:eastAsia"), "Noto Sans TC")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string("202020")
    doc.add_heading(source["title"], 0)
    doc.add_paragraph(f'{source["stage"]}　｜　{source["purpose"]}　｜　' + ("教師版" if teacher else "學生版"))
    if not teacher:
        doc.add_paragraph("班級 __________　姓名 __________　日期 __________")
    for item in source["items"]:
        if item.get("page_break"):
            doc.add_page_break()
        doc.add_heading(item["id"] + "　" + item.get("heading", "練習"), level=2)
        doc.add_paragraph(item["prompt"]).paragraph_format.keep_with_next = True
        if "formula" in item:
            doc.add_paragraph()._p.append(native_math(item["formula"]["parts"]))
        if "figure" in item:
            picture = doc.add_picture(str(assets / (item["id"] + ".png")), width=Cm(13.4))
            picture._inline.docPr.set("descr", item["figure"]["alt"])
        if "table" in item:
            rows = item["table"]
            table = doc.add_table(rows=0, cols=len(rows[0]))
            table.style = "Table Grid"
            for row in rows:
                for cell, data in zip(table.add_row().cells, row):
                    cell.text = str(data)
        if teacher and item.get("answer"):
            doc.add_paragraph(item["answer"])
        elif not teacher:
            for _ in range(item.get("answer_lines", 0)):
                doc.add_paragraph("________________________________________________________")
    doc.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--validate-only", action="store_true")
    modes.add_argument("--figures-only", action="store_true")
    modes.add_argument("--no-pdf", action="store_true")
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    validate(source)
    if args.validate_only:
        print("教材來源驗證通過")
        return
    if not args.output:
        parser.error("請指定 --output")
    soffice = None if args.no_pdf or args.figures_only else shutil.which("soffice")
    if not (args.no_pdf or args.figures_only or soffice):
        parser.error("缺少 soffice；可用 --no-pdf 產生 DOCX")
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error("請指定空白輸出目錄")
    out.mkdir(parents=True, exist_ok=True)
    for item in source["items"]:
        if "figure" in item:
            basename = out / item["id"]
            diagram(item["figure"], basename.with_suffix(".svg"),
                    None if args.figures_only else basename.with_suffix(".png"))
    if args.figures_only:
        return
    student = {key: source[key] for key in ("version", "title", "stage", "purpose", "sources") if key in source}
    student["items"] = [{key: value for key, value in item.items() if key in (
        "id", "heading", "prompt", "figure", "formula", "table", "answer_lines", "page_break"
    )} for item in source["items"]]
    student_file = out / "student.docx"
    teacher_file = out / "teacher.docx"
    document(student, student_file, out, False)
    document(source, teacher_file, out, True)
    (out / "student-source.json").write_text(json.dumps(student, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8")
    if soffice:
        with TemporaryDirectory(prefix="math-lo-") as profile:
            env = os.environ.copy()
            if sys.platform == "darwin" and not env.get("FONTCONFIG_FILE"):
                config = Element("fontconfig")
                for font_dir in (Path("/System/Library/Fonts"), Path("/Library/Fonts"),
                                 Path.home() / "Library/Fonts"):
                    SubElement(config, "dir").text = str(font_dir)
                SubElement(config, "cachedir").text = str(Path(profile) / "fonts-cache")
                path = Path(profile) / "fonts.conf"
                ElementTree(config).write(path, encoding="utf-8", xml_declaration=True)
                env["FONTCONFIG_FILE"] = str(path)
            subprocess.run([soffice, "-env:UserInstallation=" + Path(profile).as_uri(), "--headless",
                            "--convert-to", "pdf:writer_pdf_Export", "--outdir", str(out),
                            str(student_file), str(teacher_file)], check=True, env=env)
        for name in ("student.pdf", "teacher.pdf"):
            if not (out / name).is_file():
                raise RuntimeError(f"未產生 {name}")


if __name__ == "__main__":
    main()
