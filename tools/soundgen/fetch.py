"""
Downloads the recorded sources listed in sources.py into art/sounds/src/<id>/ and writes docs/LICENSES-SOUNDS.md.
Runs anywhere with python3 and curl (no pip packages). Files already present are kept, so it is safe to rerun.
Wikimedia Commons files are checked against the Commons API first and skipped unless public domain or CC0.

usage: python3 tools/soundgen/fetch.py            download what is missing, then write the licence doc
       python3 tools/soundgen/fetch.py --docs-only write the licence doc from what is already on disk
Then:  python3 tools/soundgen/build.py             (recipes switch from the procedural voice to the recordings)
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sources import AUDIO_EXT, SOURCES, commons_download, commons_page  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "art", "sounds", "src")
DOC = os.path.join(ROOT, "docs", "LICENSES-SOUNDS.md")
MANIFEST = os.path.join(SRC, "manifest.json")
UA = "TerrassicSoundFetch/1.0 (Minecraft mod build tool; github.com/RodrigoGomesDev/terrassic)"
OK_LICENCE = ("public domain", "pd-", "pd ", "cc0", "cc-zero")


def curl(url, out):
    subprocess.run(["curl", "-fsSL", "--retry", "3", "--max-time", "120", "-A", UA, "-o", out, url], check=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def audio_files(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(f for f in os.listdir(folder) if f.lower().endswith(AUDIO_EXT))


def commons_licence(name):
    """(licence short name, direct url) from the Commons API."""
    q = urllib.parse.urlencode({"action": "query", "titles": "File:" + name, "prop": "imageinfo",
                                "iiprop": "url|extmetadata", "format": "json"})
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "api.json")
        curl("https://commons.wikimedia.org/w/api.php?" + q, out)
        data = json.load(open(out, encoding="utf-8"))
    page = next(iter(data["query"]["pages"].values()))
    info = page["imageinfo"][0]
    meta = info.get("extmetadata", {})
    lic = meta.get("LicenseShortName", {}).get("value", "") or meta.get("License", {}).get("value", "")
    return lic, info["url"]


def fetch_one(sid, s):
    folder = os.path.join(SRC, sid)
    have = audio_files(folder)
    if have:
        return "ok (already here)", have
    os.makedirs(folder, exist_ok=True)
    if s["kind"] == "commons":
        lic, url = commons_licence(s["url"])
        if not any(k in lic.lower() for k in OK_LICENCE):
            return f"SKIPPED: Commons licence is '{lic}', not PD/CC0", []
        curl(url, os.path.join(folder, os.path.basename(urllib.parse.unquote(urllib.parse.urlparse(url).path))))
    elif s["kind"] == "file":
        curl(s["url"], os.path.join(folder, os.path.basename(s["url"])))
    elif s["kind"] == "zip":
        with tempfile.TemporaryDirectory() as tmp:
            z = os.path.join(tmp, "pack.zip")
            curl(s["url"], z)
            with zipfile.ZipFile(z) as zf:
                for member in zf.namelist():
                    base = os.path.basename(member)
                    if base and not base.startswith(".") and base.lower().endswith(AUDIO_EXT) and "__MACOSX" not in member:
                        with zf.open(member) as src, open(os.path.join(folder, base), "wb") as dst:
                            dst.write(src.read())
    else:
        raise ValueError(s["kind"])
    return "downloaded", audio_files(folder)


def write_doc(status):
    rows = []
    for sid, s in SOURCES.items():
        page = commons_page(s["url"]) if s["kind"] == "commons" else s.get("page", s["url"])
        files = audio_files(os.path.join(SRC, sid))
        state = status.get(sid) or ("baixado" if files else "não baixado")
        rows.append(f"| `{sid}` | {s['what']} | {s['author']} | [link]({page}) | {s['licence']} | {len(files)} | {state} |")
    text = f"""# Licenças dos sons gravados

Gerado por `tools/soundgen/fetch.py` a partir de `tools/soundgen/sources.py`. Não edite à mão.

Só entram fontes em **domínio público** ou **CC0**, baixáveis sem login:
- **PD-USGov**: gravações do governo dos EUA (National Park Service, US Fish and Wildlife Service), em domínio público. O NPS pede, por cortesia, o crédito "National Park Service", que fica aqui e nos créditos do mod.
- **CC0**: Creative Commons Zero, sem exigência de crédito, uso comercial liberado. Damos o crédito mesmo assim.

Os arquivos ficam em `art/sounds/src/<id>/`. As receitas em `tools/soundgen/recipes.py` cortam, mudam o tom e misturam esses arquivos; os sons do mod em `assets/terrassic/sounds/voice/` são derivados deles.

| Fonte | Conteúdo | Autor | Página | Licença | Arquivos | Situação |
|---|---|---|---|---|---|---|
{chr(10).join(rows)}
"""
    with open(DOC, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    status = {}
    if "--docs-only" not in sys.argv:
        manifest = {}
        for sid, s in SOURCES.items():
            try:
                state, files = fetch_one(sid, s)
            except Exception as e:  # keep going: one dead link must not block the rest
                state, files = f"FAILED: {e}", []
            status[sid] = state
            manifest[sid] = {f: sha256(os.path.join(SRC, sid, f)) for f in files}
            print(f"{sid:24s} {state} ({len(files)} files)")
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            f.write("\n")
        size = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(SRC) for fn in fns)
        print(f"art/sounds/src: {size / 1e6:.1f} MB")
    write_doc(status)
    print("wrote docs/LICENSES-SOUNDS.md")


if __name__ == "__main__":
    main()
