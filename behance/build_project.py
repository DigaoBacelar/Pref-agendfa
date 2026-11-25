#!/usr/bin/env python3
"""Prepara um projeto do Behance: imagens otimizadas + capa + textos prontos.

Uso:
    python3 behance/build_project.py <pasta_imagens> <projeto.json> [-o saida] [--zip]

projeto.json (campos):
    title        str   título do projeto
    description  str   descrição (texto longo)
    tags         list  até 10 tags
    fields       list  até 3 áreas criativas (ex.: "Branding", "Graphic Design")
    tools        list  ferramentas usadas (ex.: "Adobe Photoshop")
    order        list  (opcional) nomes de arquivo na ordem desejada
    cover        str   (opcional) arquivo usado na capa
    cover_focus  [x,y] (opcional) ponto de foco 0-1 para o corte da capa
    captions     obj   (opcional) {arquivo: legenda}
"""
import argparse, html, json, shutil, sys, zipfile
from pathlib import Path
from PIL import Image, ImageOps

PROJECT_WIDTH = 1400          # largura recomendada pelo Behance
COVER_SIZE = (808, 632)       # tamanho recomendado da capa
MAX_BYTES = 9 * 1024 * 1024   # limite do Behance é 10 MB por arquivo
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".gif"}
MAX_TAGS, MAX_FIELDS = 10, 3


def natural_key(p: Path):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def to_rgb(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, "white")
        bg.paste(img, mask=img.split()[-1])
        return bg
    return img.convert("RGB")


def save_jpeg(img: Image.Image, path: Path, quality=92):
    while True:
        img.save(path, "JPEG", quality=quality, optimize=True, progressive=True,
                 subsampling=0 if quality >= 90 else 2)
        if path.stat().st_size <= MAX_BYTES or quality <= 60:
            return quality
        quality -= 5


def make_cover(img: Image.Image, focus) -> Image.Image:
    fx, fy = focus
    tw, th = COVER_SIZE
    scale = max(tw / img.width, th / img.height)
    big = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = min(max(round(fx * big.width - tw / 2), 0), big.width - tw)
    top = min(max(round(fy * big.height - th / 2), 0), big.height - th)
    return big.crop((left, top, left + tw, top + th))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", type=Path)
    ap.add_argument("spec", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()

    spec = json.loads(a.spec.read_text(encoding="utf-8"))
    warns = []
    tags = spec.get("tags", [])
    fields = spec.get("fields", [])
    if len(tags) > MAX_TAGS:
        warns.append(f"{len(tags)} tags: Behance aceita {MAX_TAGS}; cortei o excedente.")
        tags = tags[:MAX_TAGS]
    if len(fields) > MAX_FIELDS:
        warns.append(f"{len(fields)} áreas: Behance aceita {MAX_FIELDS}; cortei o excedente.")
        fields = fields[:MAX_FIELDS]

    files = sorted([p for p in a.images.iterdir() if p.suffix.lower() in EXTS], key=natural_key)
    if spec.get("order"):
        by = {p.name: p for p in files}
        missing = [n for n in spec["order"] if n not in by]
        if missing:
            sys.exit(f"Arquivos em 'order' não encontrados: {missing}")
        rest = [p for p in files if p.name not in spec["order"]]
        files = [by[n] for n in spec["order"]] + rest
    if not files:
        sys.exit("Nenhuma imagem encontrada.")

    slug = "".join(c if c.isalnum() else "-" for c in spec["title"].lower()).strip("-")
    out = a.out or Path("behance_output") / slug
    if out.exists():
        shutil.rmtree(out)
    (out / "imagens").mkdir(parents=True)

    exported, cover_src = [], None
    for i, p in enumerate(files, 1):
        name = f"{i:02d}_{p.stem}".replace(" ", "-")
        if p.suffix.lower() == ".gif":
            dest = out / "imagens" / f"{name}.gif"
            shutil.copy(p, dest)
            w, h = Image.open(p).size
            if dest.stat().st_size > MAX_BYTES:
                warns.append(f"{p.name}: GIF acima de 10 MB, o Behance vai recusar.")
        else:
            img = to_rgb(Image.open(p))
            if img.width > PROJECT_WIDTH:
                img = img.resize((PROJECT_WIDTH, round(img.height * PROJECT_WIDTH / img.width)), Image.LANCZOS)
            elif img.width < PROJECT_WIDTH:
                warns.append(f"{p.name}: {img.width}px de largura (< {PROJECT_WIDTH}); mantive sem ampliar.")
            dest = out / "imagens" / f"{name}.jpg"
            q = save_jpeg(img, dest)
            if q < 85:
                warns.append(f"{p.name}: qualidade reduzida para {q} para caber em 10 MB.")
            w, h = img.size
            if p.name == spec.get("cover") or (cover_src is None and not spec.get("cover")):
                cover_src = img
        exported.append({"file": dest.name, "w": w, "h": h, "kb": dest.stat().st_size // 1024,
                         "caption": spec.get("captions", {}).get(p.name, "")})

    if cover_src is None:
        cover_src = to_rgb(Image.open(files[0]))
    cover = make_cover(cover_src, spec.get("cover_focus", [0.5, 0.5]))
    cover_path = out / f"capa_{COVER_SIZE[0]}x{COVER_SIZE[1]}.jpg"
    save_jpeg(cover, cover_path, 95)

    # Texto pronto para copiar/colar
    txt = [f"TÍTULO\n{spec['title']}", f"DESCRIÇÃO\n{spec.get('description', '')}",
           "TAGS (uma por vez, Enter após cada)\n" + "\n".join(tags),
           "ÁREAS CRIATIVAS (máx. 3)\n" + "\n".join(fields),
           "FERRAMENTAS\n" + "\n".join(spec.get("tools", [])),
           "ORDEM DE UPLOAD\n" + "\n".join(f"{e['file']}  ({e['w']}x{e['h']}, {e['kb']} KB)" for e in exported),
           f"CAPA\n{cover_path.name}"]
    (out / "projeto.txt").write_text("\n\n".join(txt) + "\n", encoding="utf-8")

    # Pré-visualização na ordem em que o projeto aparece no Behance
    esc = html.escape
    body = "".join(
        f'<figure><img src="imagens/{e["file"]}">' + (f'<figcaption>{esc(e["caption"])}</figcaption>' if e["caption"] else "") + "</figure>"
        for e in exported)
    (out / "preview.html").write_text(f"""<!doctype html><meta charset="utf-8"><title>{esc(spec['title'])}</title>
<style>body{{margin:0;background:#191919;color:#ddd;font:16px/1.6 system-ui,sans-serif}}
main{{max-width:{PROJECT_WIDTH}px;margin:auto}}header{{padding:48px 24px}}img{{width:100%;display:block}}
figure{{margin:0}}figcaption{{padding:12px 24px;color:#999}}.tags span{{background:#333;padding:2px 10px;border-radius:99px;margin-right:6px;font-size:13px}}</style>
<main><header><h1>{esc(spec['title'])}</h1><p>{esc(spec.get('description',''))}</p>
<p class="tags">{''.join(f'<span>{esc(t)}</span>' for t in tags)}</p></header>{body}</main>""", encoding="utf-8")

    if a.zip:
        with zipfile.ZipFile(out.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(out.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(out))

    print(f"OK: {len(exported)} imagens + capa em {out}/")
    for w in warns:
        print("AVISO:", w)


if __name__ == "__main__":
    main()
