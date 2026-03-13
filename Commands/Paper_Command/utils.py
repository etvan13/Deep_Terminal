import os
import json
import fitz

from .viewer import PdfPageItem, ImageItem, TextItem, DividerItem

# File types
PDF_EXTS  = (".pdf",)
IMG_EXTS  = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
TEXT_EXTS = (".txt", ".md", ".py", ".c", ".cpp", ".h", ".hpp", ".json", ".csv", ".log")

ATTACH_MARK = "---Attachments---"

def read_meta(proj_dir: str) -> dict:
    meta_path = os.path.join(proj_dir, "meta.json")
    if not os.path.isfile(meta_path):
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}

def list_viewables(proj_dir: str):
    files = sorted(os.listdir(proj_dir))
    out = []
    for fn in files:
        path = os.path.join(proj_dir, fn)
        if not os.path.isfile(path):
            continue

        # 🚫 skip project metadata
        if fn.lower() == "meta.json":
            continue

        low = fn.lower()
        if low.endswith(PDF_EXTS) or low.endswith(IMG_EXTS) or low.endswith(TEXT_EXTS):
            out.append(fn)
    return out

def choose_primary(meta: dict, viewables: list[str]) -> str | None:
    p = meta.get("primary")
    if isinstance(p, str) and p in viewables:
        return p

    # Prefer pdf, then img, then text
    pdfs = [f for f in viewables if f.lower().endswith(PDF_EXTS)]
    imgs = [f for f in viewables if f.lower().endswith(IMG_EXTS)]
    txts = [f for f in viewables if f.lower().endswith(TEXT_EXTS)]
    pick = (pdfs or imgs or txts)
    return pick[0] if pick else None

def resolve_order(meta: dict, primary_name: str | None, viewables: list[str]) -> list[str]:
    order = meta.get("order")
    if isinstance(order, list) and order:
        # keep only valid entries + attachment marker
        cleaned = []
        for x in order:
            if x == ATTACH_MARK:
                cleaned.append(x)
            elif isinstance(x, str) and x in viewables:
                cleaned.append(x)

        # ensure primary appears first if it exists but wasn't included
        if primary_name and primary_name in viewables and primary_name not in cleaned:
            cleaned = [primary_name] + cleaned

        # if attachments marker is present, great. if not, you still just get a flat stream.
        return cleaned or ([primary_name] if primary_name else viewables)

    # default behavior unchanged
    if primary_name and primary_name in viewables:
        rest = [f for f in viewables if f != primary_name]
        if rest:
            return [primary_name, ATTACH_MARK] + rest
        return [primary_name]
    return viewables

def scan_projects(papers_root: str, filter_text: str = ""):
    if not os.path.isdir(papers_root):
        return []

    projects = []
    for folder in sorted(os.listdir(papers_root)):
        proj_dir = os.path.join(papers_root, folder)
        if not os.path.isdir(proj_dir):
            continue

        meta = read_meta(proj_dir)
        viewables = list_viewables(proj_dir)
        if not viewables:
            continue

        title = meta.get("title") or folder
        primary_name = choose_primary(meta, viewables)
        primary_path = os.path.join(proj_dir, primary_name) if primary_name else None

        if filter_text:
            hay = (title + " " + folder + " " + " ".join(viewables)).lower()
            if filter_text.lower() not in hay:
                continue

        projects.append({
            "key": folder,
            "title": title,
            "dir": proj_dir,
            "meta": meta,
            "viewables": viewables,
            "primary_name": primary_name,
            "primary_path": primary_path,
        })

    return projects

def build_stream_items(proj: dict):
    """
    Returns (items, open_docs, title)
    open_docs is a dict[path -> fitz.Document] so we can close later.
    """
    from .viewer import PdfPageItem, ImageItem, TextItem, DividerItem  # local import to avoid circulars

    proj_dir = proj["dir"]
    meta = proj["meta"]
    viewables = proj["viewables"]
    primary_name = proj["primary_name"]
    title = meta.get("title") or proj["title"]

    order = resolve_order(meta, primary_name, viewables)

    open_docs = {}
    items = []

    def add_file(relname: str):
        path = os.path.join(proj_dir, relname)
        if not os.path.isfile(path):
            return
        low = relname.lower()

        if low.endswith(PDF_EXTS):
            doc = open_docs.get(path)
            if doc is None:
                doc = fitz.open(path)
                open_docs[path] = doc
            for pi in range(doc.page_count):
                items.append(PdfPageItem(doc, relname, pi))
            return

        if low.endswith(IMG_EXTS):
            items.append(ImageItem(path))
            return

        if low.endswith(TEXT_EXTS):
            items.append(TextItem(path, title=relname))
            return

    for entry in order:
        if entry == ATTACH_MARK:
            items.append(DividerItem("Attachments"))
        elif isinstance(entry, str):
            add_file(entry)

    return items, open_docs, title

def close_open_docs(open_docs: dict):
    for d in open_docs.values():
        try:
            d.close()
        except Exception:
            pass
