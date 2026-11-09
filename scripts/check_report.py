#!/usr/bin/env python3
"""Inspect a clinical journal club deck and its two Word companions. Python 3.8+."""
import argparse
from pathlib import Path
import posixpath
import re
import sys
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
NAV = re.compile(r"^幻灯片\s*第\s*(\d+)\s*页(?:\s|[｜|]|$)")
RED = "C00000"


def xml(part, package):
    return ET.fromstring(package.read(part))


def linked_parts(part, package):
    directory, name = posixpath.split(part)
    relpath = posixpath.join(directory, "_rels", name + ".rels")
    if relpath not in package.namelist():
        return {}
    links = {}
    for item in xml(relpath, package):
        if item.get("TargetMode") == "External":
            continue
        target = item.attrib["Target"]
        resolved = posixpath.normpath(posixpath.join(directory, target)).lstrip("/")
        links[item.attrib["Id"]] = (item.attrib["Type"].rsplit("/", 1)[-1], resolved)
    return links


def checked_package(path):
    package = ZipFile(path)
    broken = package.testzip()
    if broken:
        package.close()
        raise ValueError(f"{path.name} 包含损坏的文件 {broken}")
    return package


def inspect_slides(path):
    pages = []
    with checked_package(path) as package:
        part = "ppt/presentation.xml"
        links = linked_parts(part, package)
        for ref in xml(part, package).findall("./p:sldIdLst/p:sldId", NS):
            rid = ref.attrib["{" + NS["r"] + "}id"]
            kind, slide_part = links[rid]
            if kind != "slide":
                raise ValueError(f"无效幻灯片关系 {rid}")
            root = xml(slide_part, package)
            if root.get("show", "1").lower() in ("0", "false"):
                continue
            red_runs = [
                run for run in root.findall(".//a:r", NS)
                if run.findtext("a:t", "", NS).strip() and
                any(color.get("val", "").upper() == RED for color in
                    run.findall("a:rPr/a:solidFill/a:srgbClr", NS))
            ]
            has_notes = False
            for reltype, target in linked_parts(slide_part, package).values():
                if reltype != "notesSlide":
                    continue
                for shape in xml(target, package).findall(".//p:sp", NS):
                    placeholder = shape.find("./p:nvSpPr/p:nvPr/p:ph", NS)
                    if placeholder is not None and placeholder.get("type") == "body":
                        has_notes |= any((t.text or "").strip() for t in shape.findall(".//a:t", NS))
            pages.append((bool(red_runs), has_notes, len(root.findall(".//a:tbl", NS)),
                          len(root.findall(".//p:pic", NS))))
    if not pages:
        raise ValueError("未找到放映页")
    return pages


def inspect_word(path):
    with checked_package(path) as package:
        root = xml("word/document.xml", package)
    pages, red_pages = [], set()
    current = None
    for p in root.findall(".//w:body//w:p", NS):
        text = "".join(t.text or "" for t in p.findall(".//w:t", NS)).strip()
        match = NAV.match(text)
        if match:
            current = int(match.group(1))
            pages.append(current)
        elif text == "现场备答":
            current = None
        if current is not None:
            for run in p.findall(".//w:r", NS):
                clr = run.find("w:rPr/w:color", NS)
                if (clr is not None and clr.get("{" + NS["w"] + "}val", "").upper() == RED
                        and run.findall("w:t", NS)):
                    red_pages.add(current)
    return pages, red_pages, len(root.findall(".//w:tbl", NS)), len(root.findall(".//w:drawing", NS))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("deck", "fill", "speech"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    try:
        slides = inspect_slides(args.deck)
        expected = list(range(1, len(slides) + 1))
        red = {i for i, page in enumerate(slides, 1) if page[0]}
        print(f"PPT 放映页 {len(slides)}；含深红正文的候选页 {sorted(red)}")
        print(f"有讲者备注 {sum(p[1] for p in slides)} 页，"
              f"原生表 {sum(p[2] for p in slides)}，图片 {sum(p[3] for p in slides)}。")
        ok = True
        for label, path in (("填充稿", args.fill), ("演讲稿", args.speech)):
            pages, marked, tables, pictures = inspect_word(path)
            print(f"{label} 页段 {len(pages)}，原生表 {tables}，图片 {pictures}。")
            if pages != expected:
                print(f"{label} 的导航未对应放映页顺序：{pages}", file=sys.stderr)
                ok = False
            if marked != red:
                print(f"{label} 与 PPT 的深红页段差异：{sorted(marked ^ red)}", file=sys.stderr)
                ok = False
        return 0 if ok else 1
    except (OSError, BadZipFile, ET.ParseError, KeyError, ValueError) as exc:
        print(f"无法检查文件：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

