"""CSV / XLSX 表格读取与列名归一化。"""
from __future__ import annotations

import csv
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

_XLSX_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def normalize_header(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _is_xlsx(raw: bytes) -> bool:
    return raw[:2] == b"PK"


def _col_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return max(0, idx - 1)


def _cell_text(cell: ET.Element, shared: list[str]) -> str:
    if cell.get("t") == "s":
        value = cell.find("m:v", _XLSX_NS)
        if value is None or value.text is None:
            return ""
        idx = int(value.text)
        return shared[idx] if idx < len(shared) else ""
    if cell.get("t") == "inlineStr":
        inline = cell.find("m:is", _XLSX_NS)
        if inline is not None:
            return "".join(t.text or "" for t in inline.findall(".//m:t", _XLSX_NS))
    value = cell.find("m:v", _XLSX_NS)
    return value.text if value is not None and value.text is not None else ""


def read_xlsx_table(path: Path) -> tuple[list[str], list[list[str]]]:
    with zipfile.ZipFile(path) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall(".//m:si", _XLSX_NS):
                parts = [t.text or "" for t in si.findall(".//m:t", _XLSX_NS)]
                shared.append("".join(parts))
        sheet_name = next((n for n in zf.namelist() if n.startswith("xl/worksheets/sheet")), "")
        if not sheet_name:
            return [], []
        sheet = ET.fromstring(zf.read(sheet_name))
        matrix: list[list[str]] = []
        max_cols = 0
        for row in sheet.findall(".//m:row", _XLSX_NS):
            row_cells: dict[int, str] = {}
            for cell in row.findall("m:c", _XLSX_NS):
                ref = cell.get("r") or ""
                col = _col_index(ref) if ref else len(row_cells)
                row_cells[col] = _cell_text(cell, shared)
            if not row_cells:
                continue
            max_cols = max(max_cols, max(row_cells) + 1)
            line = [""] * max_cols
            for col, value in row_cells.items():
                if col < len(line):
                    line[col] = value
            matrix.append(line)
    if not matrix:
        return [], []
    width = max(len(r) for r in matrix)
    matrix = [r + [""] * (width - len(r)) for r in matrix]

    header_idx = 0
    for idx, row in enumerate(matrix[:40]):
        joined = " ".join(row).lower()
        if "asin" in joined and any(k in joined for k in ("spend", "cost", "acos", "花费", "available", "sku", "库存")):
            header_idx = idx
            break
    headers = [str(h).strip() for h in matrix[header_idx]]
    body = matrix[header_idx + 1 :]
    return headers, body


def read_csv_table(path: Path) -> tuple[list[str], list[list[str]]]:
    raw = path.read_bytes()
    text = ""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if not text:
        text = raw.decode("utf-8", errors="replace")

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return [], []

    header_idx = 0
    for idx, line in enumerate(lines[:20]):
        lower = line.lower()
        if "asin" in lower:
            header_idx = idx
            break

    reader = csv.reader(lines[header_idx:])
    try:
        headers = next(reader)
    except StopIteration:
        return [], []

    body: list[list[str]] = []
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        body.append(row)
    return headers, body


def read_spreadsheet_table(path: Path) -> tuple[list[str], list[list[str]]]:
    raw = path.read_bytes()
    if _is_xlsx(raw):
        return read_xlsx_table(path)
    return read_csv_table(path)


def map_headers(fieldnames: list[str], aliases: dict[str, tuple[str, ...]]) -> dict[str, int]:
    normalized = {normalize_header(name): idx for idx, name in enumerate(fieldnames)}
    mapping: dict[str, int] = {}
    for key, candidates in aliases.items():
        for alias in candidates:
            norm = normalize_header(alias)
            if norm in normalized:
                mapping[key] = normalized[norm]
                break
    return mapping


def cell(row: list[str], mapping: dict[str, int], key: str) -> str:
    idx = mapping.get(key)
    if idx is None or idx >= len(row):
        return ""
    return str(row[idx] or "").strip()
