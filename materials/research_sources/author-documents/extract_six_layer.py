#!/usr/bin/env python3
"""Локальное воспроизводимое извлечение DOCX для этапа 4.7.

Запуск из корня репозитория:
    python3 materials/research_sources/author-documents/extract_six_layer.py

Работает только со стандартной библиотекой. Не исправляет тезисы автора.
Результат является машинным переносом, а НЕ ручной сверкой этапов 4.8/4.9.
"""
from __future__ import annotations
import hashlib
import html
import posixpath
import re
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "raw" / "Шестислойная модель.docx"
OUT = ROOT / "author-documents" / "six-layer-model"
SNAP = ROOT / "snapshots" / "Шестислойная модель.extracted.md"
SHA256 = "dc53a11c90c1f6a2d7855c010f3a4f6126d39c5e75c5ccc733cb2a3430cf23fb"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
SECTIONS = [["S01",1,19,"Титульная таблица и классическая модель неокортекса"],["S02",20,40,"Формирование кластеров и связь слоёв 2 и 3"],["S03",41,63,"Реализация слоёв 2 и 3: последовательные и пространственные признаки"],["S04",64,79,"Инженерная реализация кластеров в слоях 2 и 3"],["S05",80,104,"Модуляция слоёв 2 и 3 сигналами других зон"],["S06",105,124,"Слой 5: обобщение, выбор сигнала и модуляция"],["S07",125,145,"Входы слоя 4 и локальная ошибка слоя 6"],["S08",146,163,"Слой 1 и модулирующие обратные связи"],["S09",164,181,"Сопоставление с Transformer, FFN и Mamba"],["S10",182,200,"Иерархический гистерезис, асимметрия и таблицы механизмов"],["S11",201,217,"Архитектурная модель и схемы прохождения сигналов"],["S12",218,255,"Флуктуации, закон Вебера и биологические параллели"],["S13",256,274,"Фазовое пространство градиентов и иерархия пауз"],["S14",275,309,"Функции активации с флуктуациями"],["S15",310,322,"Контрастность и селективное усиление"],["S16",323,357,"Мембранная инерция и HysteresisResidual"],["S17",358,381,"Волновые свойства и пример амплитудного гистерезиса"]]
EXPECTED_IMAGES = [[1,"B001","rId8","word/media/image1.png"],[2,"B004","rId9","word/media/image2.png"],[3,"B010","rId10","word/media/image3.png"],[4,"B016","rId11","word/media/image4.png"],[5,"B019","rId12","word/media/image5.png"],[6,"B027","rId13","word/media/image6.png"],[7,"B032","rId14","word/media/image7.png"],[8,"B035","rId15","word/media/image8.png"],[9,"B037","rId16","word/media/image9.png"],[10,"B040","rId17","word/media/image10.png"],[11,"B050","rId18","word/media/image11.png"],[12,"B058","rId19","word/media/image12.png"],[13,"B062","rId20","word/media/image13.png"],[14,"B066","rId21","word/media/image14.png"],[15,"B079","rId22","word/media/image15.png"],[16,"B086","rId23","word/media/image16.png"],[17,"B088","rId24","word/media/image17.png"],[18,"B090","rId25","word/media/image18.png"],[19,"B091","rId26","word/media/image19.png"],[20,"B097","rId27","word/media/image20.png"],[21,"B104","rId28","word/media/image21.png"],[22,"B114","rId29","word/media/image22.png"],[23,"B120","rId30","word/media/image23.png"],[24,"B125","rId31","word/media/image24.png"],[25,"B135","rId32","word/media/image25.png"],[26,"B146","rId33","word/media/image26.png"],[27,"B164","rId34","word/media/image27.png"],[28,"B166","rId35","word/media/image28.png"],[29,"B176","rId36","word/media/image29.png"],[30,"B183","rId37","word/media/image30.png"],[31,"B208","rId38","word/media/image31.png"],[32,"B210","rId39","word/media/image32.png"],[33,"B212","rId40","word/media/image33.png"],[34,"B214","rId41","word/media/image34.png"],[35,"B216","rId42","word/media/image35.png"],[36,"B229","rId43","word/media/image36.png"],[37,"B237","rId44","word/media/image37.png"],[38,"B246","rId45","word/media/image38.png"],[39,"B250","rId46","word/media/image39.png"],[40,"B257","rId47","word/media/image40.png"],[41,"B265","rId48","word/media/image41.png"],[42,"B266","rId49","word/media/image42.png"],[43,"B267","rId50","word/media/image43.png"],[44,"B281","rId51","word/media/image44.png"],[45,"B286","rId52","word/media/image45.png"],[46,"B309","rId53","word/media/image46.png"],[47,"B311","rId54","word/media/image47.png"],[48,"B313","rId55","word/media/image48.png"],[49,"B314","rId56","word/media/image49.png"],[50,"B315","rId57","word/media/image50.png"],[51,"B316","rId58","word/media/image51.png"],[52,"B317","rId59","word/media/image52.png"],[53,"B322","rId60","word/media/image53.png"],[54,"B348","rId61","word/media/image54.png"],[55,"B377","rId62","word/media/image55.png"],[56,"B379","rId63","word/media/image56.png"]]
EXPECTED_TABLES = [[1,"B001"],[2,"B192"],[3,"B200"]]

def quoted(value):
    return html.escape(value, quote=True)

def text_of(node):
    return "".join((child.text or "") if child.tag == W+"t" else
                   "\t" if child.tag == W+"tab" else
                   "\n" if child.tag in (W+"br", W+"cr") else ""
                   for child in node.iter())

def run_html(run):
    parts = []
    for element in run.iter():
        if element.tag == W+"t":
            parts.append(quoted(element.text or ""))
        elif element.tag == W+"tab":
            parts.append("&#9;")
        elif element.tag in (W+"br", W+"cr"):
            parts.append("<br>")
    value = "".join(parts)
    if not value:
        return ""
    props = run.find(W+"rPr")
    if props is not None:
        for name, tag in (("b", "strong"), ("i", "em"), ("u", "u")):
            item = props.find(W+name)
            if item is not None and item.get(W+"val") not in ("0", "false", "off"):
                value = "<"+tag+">"+value+"</"+tag+">"
        valign = props.find(W+"vertAlign")
        if valign is not None and valign.get(W+"val") in ("superscript", "subscript"):
            tag = "sup" if valign.get(W+"val") == "superscript" else "sub"
            value = "<"+tag+">"+value+"</"+tag+">"
    return value

def paragraph_markup(paragraph, block_id, archive, relations, figures):
    inline = []
    images = []
    # Runs may be children of hyperlinks. Preserve display text, not unverified URLs.
    for run in paragraph.iter(W+"r"):
        inline.append(run_html(run))
        for blip in run.iter(A+"blip"):
            rid = blip.get(R+"embed")
            if rid:
                images.append(rid)
    pstyle = paragraph.find("./"+W+"pPr/"+W+"pStyle")
    style = pstyle.get(W+"val", "") if pstyle is not None else ""
    body = "".join(inline)
    kind = "h3" if re.match(r"Heading[1-9]", style) else "p"
    out = ["<"+kind+' id="'+block_id+'">'+body+"</"+kind+">"]
    for rid in images:
        if rid not in relations:
            raise ValueError("Unknown image relationship "+rid+" in "+block_id)
        target = relations[rid]
        media = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("word", target))
        if not media.startswith("word/media/"):
            raise ValueError("Unexpected image target "+media)
        index = len(figures)+1
        expected = EXPECTED_IMAGES[index-1] if index <= len(EXPECTED_IMAGES) else None
        if expected is None or (expected[1], expected[2], expected[3]) != (block_id, rid, media):
            raise ValueError("Image sequence mismatch at "+block_id+" "+rid+" "+media)
        name = "image"+str(index)+".png"
        (OUT/"media").mkdir(parents=True, exist_ok=True)
        (OUT/"media"/name).write_bytes(archive.read(media))
        figures.append((index, block_id, rid, media))
        out.append('<figure id="figure-'+str(index)+'"><img src="media/'+name+'" alt="Изображение '+str(index)+' из документа" loading="lazy"><figcaption>Изображение '+str(index)+', исходный блок '+block_id+'. Оригинальная подпись проверяется в 4.9.</figcaption></figure>')
    return "\n".join(out)

def table_markup(table, block_id, number, archive, relations, figures):
    rows = []
    for tr in table.findall(W+"tr"):
        cells = []
        for tc in tr.findall(W+"tc"):
            inner = []
            for node in tc:
                if node.tag == W+"p":
                    inner.append(paragraph_markup(node, block_id, archive, relations, figures).replace(' id="'+block_id+'"', ""))
                elif node.tag == W+"tbl":
                    inner.append("<p>"+quoted(text_of(node))+"</p>")
            span = tc.find("./"+W+"tcPr/"+W+"gridSpan")
            colspan = (' colspan="'+quoted(span.get(W+"val", "1"))+'"') if span is not None else ""
            cells.append("<td"+colspan+">"+"\n".join(inner)+"</td>")
        rows.append("<tr>"+"".join(cells)+"</tr>")
    return '<div id="'+block_id+'" class="table-wrapper"><table id="table-'+str(number)+'"><tbody>'+"\n".join(rows)+"</tbody></table></div>"

def main():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SHA256:
        raise SystemExit("SHA-256 mismatch for DOCX: "+digest)
    OUT.mkdir(parents=True, exist_ok=True)
    with ZipFile(SOURCE) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        rels = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
        relations = {x.get("Id"): x.get("Target") for x in rels.findall(REL+"Relationship")}
        body = document.find(W+"body")
        blocks = [x for x in body if x.tag != W+"sectPr"]
        if len(blocks) != 381:
            raise SystemExit("Expected 381 blocks, got "+str(len(blocks)))
        figures, table_positions, fragments, records = [], [], [], []
        for section_id, first, last, title in SECTIONS:
            fragments.append('<section id="'+section_id+'"><h2>'+quoted(section_id+". "+title)+'</h2>')
            for index in range(first, last+1):
                block = blocks[index-1]
                bid = "B"+str(index).zfill(3)
                current_figures = len(figures)
                if block.tag == W+"p":
                    fragment = paragraph_markup(block, bid, archive, relations, figures)
                elif block.tag == W+"tbl":
                    table_positions.append((len(table_positions)+1, bid))
                    fragment = table_markup(block, bid, len(table_positions), archive, relations, figures)
                else:
                    fragment = '<span id="'+bid+'"></span>'
                fragments.append(fragment)
                text = text_of(block).replace("\n", " ").strip()
                refs = ["figure-"+str(item[0]) for item in figures[current_figures:]]
                if block.tag == W+"tbl":
                    refs.append("table-"+str(len(table_positions)))
                records.append((bid, section_id, text, refs))
            fragments.append("</section>")
    if len(figures) != 56 or len(table_positions) != 3:
        raise SystemExit("Media/table counts mismatch: "+str((len(figures), len(table_positions))))
    if table_positions != [(t[0], t[1]) for t in EXPECTED_TABLES]:
        raise SystemExit("Table positions mismatch: "+str(table_positions))
    top = """<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Шестислойная модель</title><link rel="stylesheet" href="../document.css"></head><body>
<header><h1>Шестислойная модель</h1><p>Неокортекс и нейронные сети · редакция 3, 08.05.2025</p></header>
<aside>Автоматическое извлечение из авторского DOCX; список разделов и все 381 якорь зафиксированы. В 4.8–4.9 выполняется сверка текста, формул, списков, подписей, изображений и таблиц. <a href="../../raw/%D0%A8%D0%B5%D1%81%D1%82%D0%B8%D1%81%D0%BB%D0%BE%D0%B9%D0%BD%D0%B0%D1%8F%20%D0%BC%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C.docx">Оригинал DOCX</a> · <a href="mapping.md">Соответствия</a></aside>
<nav aria-label="Оглавление"><ol>"""
    top += "".join('<li><a href="#'+sid+'">'+quoted(sid+": "+title)+'</a></li>' for sid, start, end, title in SECTIONS)
    top += "</ol></nav><main>"
    (OUT/"index.html").write_text(top+"\n".join(fragments)+"</main></body></html>\n", encoding="utf-8")
    snapshot = ["# Шестислойная модель — машинный поисковый снимок",
                "Источник: raw/Шестислойная модель.docx, SHA-256: "+SHA256,
                "Автоматическое извлечение: визуальная сверка и формулы — 4.8/4.9.", ""]
    for bid, group, txt, refs in records:
        snapshot.extend(["## "+bid+" ("+group+")", txt or "(нет текстовых узлов)", "Объекты: "+(", ".join(refs) if refs else "—"), ""])
    SNAP.write_text("\n".join(snapshot), encoding="utf-8")
    # Проверяем непрерывность и отсутствие дублирующих якорей в HTML.
    markup = (OUT/"index.html").read_text(encoding="utf-8")
    for index in range(1, 382):
        bid = "B"+str(index).zfill(3)
        if markup.count('id="'+bid+'"') != 1:
            raise SystemExit("Invalid anchor "+bid)
    print("Extracted: 381 blocks, 56 PNG, 3 tables; snapshot and HTML written")
    print("Review still required: S01–S17 and V01–V10")

if __name__ == "__main__":
    main()
