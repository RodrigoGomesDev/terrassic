"""Entregas 1 e 3: uma folha por espécie (as três blocagens de lado e de 3/4, com a pessoa de 1,70 m) e o teste de
reconhecimento (a blocagem escolhida de cada espécie ao lado dos herbívoros do jogo que se parecem).

uso: python -B folhas.py [maiasaura corythosaurus pachyrhinosaurus thescelosaurus]
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sil  # noqa: E402
import sheet  # noqa: E402

OUT = "/Users/rodrigogs/projects/terrassic/Claude outputs/silhuetas-1.11/img"
SPECIES = ["maiasaura", "corythosaurus", "pachyrhinosaurus", "thescelosaurus"]
# os herbívoros do jogo que se parecem com eles (a métrica compara contra estes e contra as outras variantes novas)
NEIGHBOURS = [("edmontosaurus", "Edmontossauro"), ("parasaurolophus", "Parassaurolofo"),
              ("triceratops", "Tricerátops"), ("styracosaurus", "Estiracossauro")]
# a checagem larga: o mais parecido entre todos os refeitos do jogo que andam em terra (o número da resposta)
BROAD = [("pachycephalosaurus", "Paquicefalossauro"), ("gallimimus", "Galimimo"), ("velociraptor", "Velociraptor"),
         ("dakotaraptor", "Dakotaraptor"), ("ankylosaurus", "Anquilossauro"), ("protoceratops", "Protocerátops"),
         ("therizinosaurus", "Terizinossauro"), ("tyrannosaurus", "T. rex"), ("quetzalcoatlus", "Quetzalcoatlus")]
OLD = {"maiasaura": "Maiassauro (hoje)", "corythosaurus": "Coritossauro (hoje)"}
PICK = {"maiasaura": "C", "corythosaurus": "B", "pachyrhinosaurus": "B", "thescelosaurus": "A"}
PPM = {"thescelosaurus": 110}


def neighbours():
    out = {}
    for sp, n in NEIGHBOURS + [(k, v) for k, v in OLD.items()] + BROAD:
        spec = sil.load_game(sp)
        out[n] = (spec, sil.signature(spec))
    return out


def variants(sp):
    mod = importlib.import_module(sp)
    res = []
    for key, short, trait, fn in mod.VARIANTS:
        spec = fn().spec()
        res.append((key, short, trait, spec, sil.signature(spec)))
    return mod, res


NARROW = set(n for _s, n in NEIGHBOURS) | set(OLD.values())


def closest(sig, refs, skip=(), only=None):
    return max((sil.similarity(sig, s), n) for n, (_sp, s) in refs.items()
               if n not in skip and (only is None or n in only))


def species_sheet(sp, refs, log):
    mod, vs = variants(sp)
    ppm = PPM.get(sp, 52)
    rows = []
    for key, short, trait, spec, sig in vs:
        sim, who = closest(sig, refs, only=NARROW)
        bsim, bwho = closest(sig, refs)
        log.append((mod.NAME, key, short, sim, who, "| todos os refeitos:", bsim, bwho))
        a = sheet.row([(spec, "", "")], ppm, sil.SIDE, label_h=4)
        b = sheet.row([(spec, "", "")], ppm, sil.TQ, label_h=4)
        rows.append(caption(side_by_side(a, b), f"{key}. {short}", trait,
                            f"semelhança de silhueta {sim:.2f} com o mais parecido dos herbívoros vizinhos ({who}); "
                            f"entre todos os refeitos de terra: {bsim:.2f} ({bwho})"))
    img = sheet.stack(rows, f"{mod.NAME}, \"{mod.THEME}\": três blocagens (de lado e de 3/4)",
                      "Cubos em preto no tamanho real; a figura azul é uma pessoa de 1,70 m. Semelhança 0..1 contra os "
                      "bicos-de-pato e ceratopsianos do jogo.")
    n = SPECIES.index(sp) + 1
    img.save(os.path.join(OUT, f"01_{n}_{sp}_variantes.png"))
    return vs


def wrap(text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) > width and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    return lines + [cur]


def caption(img, title, trait, sim):
    from PIL import Image, ImageDraw
    f1, f2, f3 = sil.font(22, True), sil.font(17), sil.font(16)
    width = max(img.width - 48, 900)
    tl, sl = wrap(trait, f2, width), wrap(sim, f3, width)
    out = Image.new("RGB", (max(img.width, width + 48), img.height + 40 + 24 * len(tl) + 22 * len(sl)), sheet.BG)
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    y = img.height + 2
    d.text((24, y), title, fill=sheet.TEXT, font=f1); y += 32
    for ln in tl:
        d.text((24, y), ln, fill=sheet.TEXT, font=f2); y += 24
    for ln in sl:
        d.text((24, y), ln, fill=sheet.SUB, font=f3); y += 22
    return out


def side_by_side(a, b, gap=30):
    from PIL import Image
    out = Image.new("RGB", (a.width + gap + b.width, max(a.height, b.height)), sheet.BG)
    out.paste(a, (0, out.height - a.height)); out.paste(b, (a.width + gap, out.height - b.height))
    return out


def recognition(all_vs, refs, log):
    picks = []
    sigs = {}
    for sp in SPECIES:
        mod = importlib.import_module(sp)
        key, short, trait, spec, sig = next(v for v in all_vs[sp] if v[0] == PICK[sp])
        picks.append((mod.NAME, key, short, spec, sig))
        sigs[f"{mod.NAME} {key}"] = (spec, sig)
    pool = dict(sigs); pool.update({n: refs[n] for _s, n in NEIGHBOURS})
    items = []
    for name, key, short, spec, sig in picks:
        sim, who = closest(sig, pool, skip=(f"{name} {key}",))
        items.append((spec, f"{name} {key}", f"{short}; {sim:.2f} x {who}"))
        log.append(("RECON", name, key, sim, who))
    for sp, n in NEIGHBOURS:
        spec, sig = refs[n]
        sim, who = closest(sig, pool, skip=(n,))
        items.append((spec, n, f"do jogo; {sim:.2f} x {who}"))
    a = sheet.row(items[:4], 34, sil.SIDE, label_h=56, title_font=18, sub_font=13)
    b = sheet.row(items[4:], 34, sil.SIDE, label_h=56, title_font=18, sub_font=13)
    c = sheet.row([(s, "", "") for s, _t, _u in items], 24, sil.TQ, label_h=10)
    img = sheet.stack([a, b, c], "Teste de reconhecimento: sem cor, cada um tem que ser reconhecível",
                      "Em cima, as blocagens recomendadas; no meio, os herbívoros do jogo que se parecem; embaixo, todos "
                      "de 3/4. Número = semelhança de silhueta com o mais parecido do grupo (0..1).")
    img.save(os.path.join(OUT, "03_reconhecimento.png"))


if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("-")] or SPECIES
    refs = neighbours()
    log, all_vs = [], {}
    for sp in want:
        all_vs[sp] = species_sheet(sp, refs, log)
    if set(all_vs) == set(SPECIES):
        recognition(all_vs, refs, log)
    for r in log:
        print(" | ".join(f"{x:.3f}" if isinstance(x, float) else str(x) for x in r))
