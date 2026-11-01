"""
Vozes no estilo ARK (2026-11): ambient, threat, hurt e death de cada espécie.

O ARK (Studio Wildcard) foi só a RÉGUA: medimos os sons dele fora do repositório (duração, brilho, energia por
faixa) e ajustamos as nossas vozes a esses números. Nenhum som do ARK está aqui nem no mod.

Feitas de trechos de gravações de domínio público / CC0 de art/sounds/src (alce, urso-pardo, jacaré, bisão, grou,
garça, pelicano: fontes e licenças em docs/LICENSES-SOUNDS.md), desaceleradas e misturadas, mais síntese própria:
ar rasgado de garganta que segue o volume da voz, grave profundo, saturação e sala.

Cuidados que o ouvido do Rodrigo pediu:
  - nada de "moto": o volume não pode pulsar em ritmo fixo (alisar tira o pulsar de 10-120 Hz que o alce ganha
    desacelerado; a aspereza é irregular). Medida: pulsing() < 4 (ruído puro ~2,8).
  - o grave não pode virar uma nota limpa (tonalidade grave baixa).

build.py chama render(sid, event, v). Sem as gravações baixadas (fetch.py), build.py mantém os .ogg já gerados.
"""
import json
import os
import subprocess

import numpy as np

from synth import SR, drive, envelope, noise, norm, reverb, smooth, spectral_filter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "art", "sounds", "src")
FILES = {"elk": "nps_elk_bugle/nri-ElkBuglingGRSA.mp3", "griz": "nps_grizzly_roar/yell-YELLgrizzlyC20160626SM303143.mp3",
         "grizw": "nps_grizzly_warn/yell-YELLGrizzlyBearVocalizations20160520Android1.mp3",
         "bisa": "nps_bison_bellow_a/yell-YELLMM8K2005914Bison.mp3", "bisb": "nps_bison_bellow_b/yell-YELLMM8K2005918Bison.mp3",
         "crane": "nps_crane/yell-YELLFLBCSACR20075171.mp3", "raven": "nps_raven/yell-RavenBlackSandBasin.mp3",
         "alli": "wm_alligator_bellow/Alligatorbellow1.ogg", "alli2": "wm_alligator_bellow_2/27alligator2bellow.ogg",
         "hiss": "wm_alligator_hiss/Alligatorhiss.ogg", "heron": "wm_heron/Littleblueheronfishes.ogg",
         "pelican": "wm_pelican/Baby_pelican.ogg", "bear1": "oga_bear/bear_01.ogg", "bear2": "oga_bear/bear_02.ogg"}
# trechos altos de cada gravação (início, fim em segundos), achados automaticamente
GRAINS = json.load(open(os.path.join(HERE, "arkstyle_grains.json")))
EVENTS = ("ambient", "threat", "hurt", "death")
COUNT = {"ambient": 3, "threat": 2, "hurt": 2, "death": 1}


def needed_files():
    return sorted({os.path.join(SRC, FILES[k]) for k in FILES})


def available():
    return all(os.path.exists(p) for p in needed_files())


_audio, _grain = {}, {}


def load(name):
    if name not in _audio:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SRC, FILES[name]), "-ac", "1", "-ar", str(SR),
                              "-f", "f32le", "-"], capture_output=True, check=True).stdout
        _audio[name] = np.frombuffer(raw, "<f4").astype(float)
    return _audio[name]


def denoise(x, floor_db=-30):
    """portão espectral: tira o ruído de campo constante (vento, chiado) debaixo do animal"""
    n = 2048; h = 512; w = np.hanning(n)
    pad = np.concatenate([np.zeros(n), x, np.zeros(n)])
    S = np.array([np.fft.rfft(pad[i:i + n] * w) for i in range(0, len(pad) - n, h)]); mag = np.abs(S)
    floor = np.percentile(mag, 15, axis=0)
    g = np.clip((mag - 1.5 * floor) / (mag + 1e-9), 10 ** (floor_db / 20), 1)
    Y = np.fft.irfft(S * g, n, axis=1) * w
    out = np.zeros(len(pad)); ws = np.zeros(len(pad))
    for k, i in enumerate(range(0, len(pad) - n, h)):
        out[i:i + n] += Y[k]; ws[i:i + n] += w ** 2
    return (out / np.maximum(ws, 1e-3))[n:n + len(x)]


def _lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def alisar(x, fast=120.0, slow=10.0, amount=1.0):
    """tira o pulsar REGULAR do volume (efeito moto): divide pela envoltória rápida e multiplica pela lenta"""
    if len(x) < SR // 20:
        return x
    a = np.abs(x) + 1e-6
    g = np.clip(np.maximum(_lp(a, slow), 1e-4) / np.maximum(_lp(a, fast), 1e-4), 0.25, 4.0) ** amount
    return x * g


def aspero(n, rate, rng):
    """aspereza irregular (ruído filtrado em volta de rate), sem período fixo"""
    m = _lp(rng.standard_normal(n), rate * 1.5) - _lp(rng.standard_normal(n), rate * 0.3)
    return np.clip(0.5 + 1.2 * m / (np.abs(m).max() + 1e-9), 0, 1)


def pulsing(x):
    """quanto o volume pulsa em ritmo fixo (15-80 Hz) no trecho mais alto; ruído puro dá ~2,8"""
    k = int(SR / 400); e = np.convolve(np.abs(x), np.ones(k) / k, "same")[::k]; fs = SR / k
    pk = np.argmax(np.convolve(np.abs(x), np.ones(SR // 10), "same")); a = max(0, int(pk / k - fs)); e = e[a:a + int(2 * fs)]
    e = e - e.mean(); E = np.abs(np.fft.rfft(e * np.hanning(len(e)))); f = np.fft.rfftfreq(len(e), 1 / fs)
    i = np.argmax(E * ((f > 15) & (f < 80)))
    return float(E[i] / np.median(E[(f > 2) & (f < 150)]))


def grain(name, idx):
    key = (name, idx)
    if key not in _grain:
        a, b = GRAINS[name][idx]; x = load(name)
        y = x[max(0, int((a - 0.05) * SR)):min(len(x), int((b + 0.1) * SR))]
        _grain[key] = norm(denoise(y - y.mean()), 1.0)
    return _grain[key]


def take(g, out_dur, speed, start=0.0, ramp=(1.0, 1.0), fi=0.03, fo=0.4):
    """trecho do grão tocado a `speed` (<1 = mais lento e grave), com rampa de velocidade, até out_dur segundos"""
    x = grain(*g)
    n = int(out_dur * SR); r = speed * np.linspace(ramp[0], ramp[1], n)
    pos = start * len(x) + np.cumsum(r); pos = pos[pos < len(x) - 1]
    if len(pos) < SR * 0.05:
        pos = np.cumsum(r)[:len(x) - 1]
    y = alisar(alisar(np.interp(pos, np.arange(len(x)), x)))
    return norm(y * envelope(len(y), fi, min(fo, 0.9 * len(y) / SR), 1.0), 1.0)


def place(parts, n=None):
    out = np.zeros(max(max(int(s * SR) + len(x) for s, x, g in parts), n or 0))
    for s, x, g in parts:
        i = int(s * SR); out[i:i + len(x)] += g * x
    return out


def throat_air(voice, rng, rasp, rate, k, gain_hi=0.0):
    """ar rasgado que segue o volume da voz, com aspereza irregular"""
    n = len(voice); env = smooth(np.abs(voice), int(SR * 0.04)); env /= env.max() + 1e-9
    a = noise(n, rng, 0.4) * ((1 - rasp) + rasp * aspero(n, rate, rng))
    a = spectral_filter(a, ((520 * k, 450 * k, 0), (1250 * k, 800 * k, -2), (2600 * k, 1400 * k, -6 + gain_hi),
                            (4200 * k, 1800 * k, -10 + gain_hi)), floor=0.02)
    return norm(a * env ** 1.3, 1.0)


def rumble(n, rng, lp=85):
    x = spectral_filter(noise(n, rng, 2.0), (), floor=1.0, hp=22, lp=lp)
    return norm(x * envelope(n, min(0.6, n / SR / 3), min(1.5, n / SR / 2), 1.0), 1.0)


DEF = dict(k=1.0, scream=[], growl=[], low=[], bark=None, g=dict(scream=0.7, growl=0.8, low=0.6, bark=0.5, air=1.0,
           rumble=0.0, hiss=0.0), rasp=0.6, rate=38, airk=1.0, body=2.0, drv=3.0, room=(1.8, 0.2), lp=9500, hi=0.0)


def prof(**kw):
    p = {**DEF, **kw}; p["g"] = {**DEF["g"], **kw.get("g", {})}
    return p


def _mix(p, parts, n, rng, air_gain, rumble_gain, lp, drv, room, hiss_gain=0.0, rmb_lp=85):
    voice = place(parts, n)
    tail = int(0.3 * SR); voice = np.concatenate([voice, np.zeros(tail)])
    lay = [(0, voice, 1.0)]
    if air_gain > 0: lay.append((0, throat_air(voice, rng, p["rasp"], p["rate"], p["airk"], p["hi"]), air_gain))
    if rumble_gain > 0: lay.append((0, rumble(len(voice), rng, rmb_lp), rumble_gain))
    if hiss_gain > 0:
        h = take(("hiss", 0), len(voice) / SR, 1.0, start=rng.uniform(0, 0.5), fi=0.1, fo=0.4)
        h = np.concatenate([h, np.zeros(max(0, len(voice) - len(h)))])[:len(voice)]
        lay.append((0, h * (smooth(np.abs(voice), int(SR * 0.05)) / (np.abs(voice).max() + 1e-9)) ** 0.5, hiss_gain))
    x = alisar(place(lay), amount=0.7)
    x = spectral_filter(x, (), floor=1.0, hp=22, lp=lp); x = drive(x, drv); x = reverb(x, *room)
    return norm(x, 0.9)

def _pick(lst, v):
    return lst[v % len(lst)] if lst else None

def threat(p, v=0):
    rng = np.random.default_rng(100 + v); k = p["k"]; g = p["g"]; body = p["body"]
    lo = _pick(p["low"], v); intro = min(0.8, 0.3 * body) if lo else 0.0; parts = []
    if lo: parts.append((0.0, take(lo[:2], intro + 0.2, lo[2] * k, start=0.1 * v, fi=0.6 * intro, fo=0.15), g["low"]))
    if p["bark"]: parts.append((max(0, intro - 0.05), take(p["bark"][:2], 1.2, p["bark"][2] * k, fi=0.005, fo=0.5), g["bark"]))
    for i, s in enumerate(p["scream"]):
        parts.append((intro + 0.1, take(s[:2], body, s[2] * k, start=0.08 * v, fi=0.12, fo=0.5), g["scream"] / (1 + 0.6 * i)))
    for i, s in enumerate(p["growl"]):
        parts.append((intro, take(s[:2], body + 0.4, s[2] * k, start=0.1 * v, fi=0.04, fo=0.5), g["growl"] / (1 + 0.6 * i)))
    n = int((intro + body + 0.4) * SR)
    return _mix(p, parts, n, rng, g["air"], g["rumble"], p["lp"], p["drv"], p["room"], g["hiss"])

def ambient(p, v=0):
    """chamado de boca meio fechada: mais grave e escuro, sem o grito aberto"""
    rng = np.random.default_rng(200 + v); k = p["k"]; g = p["g"]; d = max(0.6, 0.6 * p["body"]); parts = []
    for i, s in enumerate(p["growl"] + p["low"]):
        parts.append((0.0, take(s[:2], d, s[2] * k * 0.95, start=0.15 + 0.2 * v, fi=0.2 * d, fo=0.45 * d), g["growl"] / (1 + 0.7 * i)))
    for i, s in enumerate(p["scream"][:1]):
        parts.append((0.1 * d, take(s[:2], d * 0.8, s[2] * k * 0.92, start=0.3 + 0.15 * v, fi=0.25 * d, fo=0.4 * d), 0.35 * g["scream"]))
    lp = min(p["lp"], 4200 * k ** 0.5)
    return _mix(p, parts, int(d * SR), rng, 0.5 * g["air"], g["rumble"] * 0.8, lp, max(1.2, p["drv"] * 0.6),
                (p["room"][0] * 0.8, p["room"][1]), 0.5 * g["hiss"])

def hurt(p, v=0):
    rng = np.random.default_rng(300 + v); k = p["k"]; g = p["g"]; d = float(np.clip(0.18 * p["body"] + 0.25, 0.3, 0.75)); parts = []
    for i, s in enumerate(p["scream"][:2]):
        parts.append((0.0, take(s[:2], d, s[2] * k * 1.15, start=0.2 + 0.25 * v, fi=0.004, fo=0.6 * d), g["scream"] * 1.2 / (1 + 0.6 * i)))
    for i, s in enumerate(p["growl"][:1]):
        parts.append((0.0, take(s[:2], d, s[2] * k * 1.1, start=0.3 + 0.2 * v, fi=0.004, fo=0.6 * d), g["growl"]))
    if p["bark"]: parts.append((0.0, take(p["bark"][:2], d, p["bark"][2] * k * 1.1, fi=0.003, fo=0.5 * d), g["bark"]))
    return _mix(p, parts, int(d * SR), rng, g["air"], 0.3 * g["rumble"], p["lp"], p["drv"] * 1.2,
                (p["room"][0] * 0.6, p["room"][1] * 0.8), g["hiss"])

def death(p, v=0):
    """grito que perde força e cai de tom, terminando num sopro"""
    rng = np.random.default_rng(400 + v); k = p["k"]; g = p["g"]; d = max(1.2, 0.6 * p["body"] + 0.8); parts = []
    for i, s in enumerate(p["scream"][:2]):
        parts.append((0.0, take(s[:2], d, s[2] * k, start=0.1, ramp=(1.05, 0.6), fi=0.05, fo=0.6 * d), g["scream"] / (1 + 0.6 * i)))
    for i, s in enumerate(p["growl"][:1] + p["low"][:1]):
        parts.append((0.05, take(s[:2], d + 0.3, s[2] * k, start=0.2, ramp=(1.0, 0.55), fi=0.05, fo=0.7 * d), g["growl"] / (1 + 0.6 * i)))
    x = parts; n = int((d + 0.6) * SR)
    return _mix(p, x, n, rng, 1.2 * g["air"], 0.7 * g["rumble"], p["lp"] * 0.8, p["drv"] * 0.8,
                (p["room"][0] * 1.1, p["room"][1] * 1.2), g["hiss"])


# ---------------------------------------------------------------- espécies
# grão = (gravação, índice do trecho em graos.json, velocidade base; <1 = mais lento e grave)
ELK, ELK2 = ("elk", 1), ("elk", 3)
GRIZ, GRIZ2 = ("griz", 1), ("griz", 2)
GW_LO, GW_LO2, GW_HI = ("grizw", 9), ("grizw", 4), ("grizw", 14)
BISA, BISB, BISB2 = ("bisa", 1), ("bisb", 0), ("bisb", 5)
CRANE, CRANE2, CRANE3 = ("crane", 1), ("crane", 5), ("crane", 7)
ALLI, ALLI_B, ALLI2 = ("alli", 1), ("alli", 2), ("alli2", 0)
HERON, HERON2 = ("heron", 4), ("heron", 6)
PEL = ("pelican", 0)
BEAR1, BEAR2 = ("bear1", 0), ("bear2", 0)
def g(x, s):
    return (*x, s)

BIG = dict(low=[g(ALLI, 0.85)], bark=g(BISA, 0.75), rasp=0.7, body=4.0, drv=3.0, room=(2.2, 0.22),
           g=dict(scream=0.7, growl=0.8, low=0.6, air=1.0, rumble=0.9))
P = {
    # grandes terópodes: o T. rex é a versão E aprovada; os outros são primos dela
    "tyrannosaurus": (prof(**BIG, scream=[g(ELK, 0.42)], growl=[g(GRIZ, 0.9)]), "Rexsound"),
    "tarbosaurus": (prof(**{**BIG, "k": 1.08}, scream=[g(ELK2, 0.42)], growl=[g(GRIZ2, 0.9)]), "Rexsound"),
    "daspletosaurus": (prof(**BIG, scream=[g(ELK, 0.45)], growl=[g(GW_LO, 0.95), g(GRIZ, 0.9)]), "Yutyrannussound"),
    "albertosaurus": (prof(**{**BIG, "k": 1.15, "body": 3.0}, scream=[g(CRANE, 0.7), g(ELK, 0.45)], growl=[g(BEAR1, 0.7)]), "S_allosaurus_startled"),
    "giganotosaurus": (prof(**{**BIG, "k": 0.92, "rasp": 0.85, "hi": 3.0}, scream=[g(ELK2, 0.42), g(PEL, 0.35)], growl=[g(GRIZ2, 0.85)]), "Gigasound"),
    "carcharodontosaurus": (prof(**{**BIG, "k": 0.95}, scream=[g(ELK, 0.4)], growl=[g(GW_LO2, 0.9), g(GRIZ, 0.85)]), "Carchasound"),
    "spinosaurus": (prof(**{**BIG, "low": [g(ALLI2, 0.8)], "g": dict(BIG["g"], hiss=0.25)}, scream=[g(ELK2, 0.45)], growl=[g(ALLI_B, 0.85)]), "Spinosound"),
    # terópodes médios
    "carnotaurus": (prof(scream=[g(PEL, 0.45)], growl=[g(BEAR1, 0.6)], low=[g(ALLI, 0.9)], bark=g(BISB, 0.8), body=2.4,
                         g=dict(rumble=0.4)), "Carnosound"),
    "majungasaurus": (prof(k=1.08, scream=[g(PEL, 0.45)], growl=[g(BEAR2, 0.6)], low=[g(ALLI_B, 0.9)], bark=g(BISB, 0.8), body=2.2,
                           g=dict(rumble=0.3)), "Carnosound"),
    "dilophosaurus": (prof(scream=[g(HERON, 0.75), g(PEL, 0.8)], growl=[g(BEAR2, 1.0)], body=1.6, rate=50, room=(1.4, 0.18),
                           g=dict(hiss=0.5)), "Dilosound"),
    # raptores
    "velociraptor": (prof(scream=[g(CRANE, 0.9), g(CRANE2, 0.9)], growl=[g(BEAR1, 1.1)], low=[g(GW_LO, 1.2)], body=1.4, rate=48,
                          rasp=0.75, room=(1.3, 0.16)), "Raptorsound3"),
    "dakotaraptor": (prof(k=0.92, scream=[g(CRANE, 0.9), g(CRANE2, 0.9)], growl=[g(BEAR1, 1.1)], low=[g(GW_LO, 1.2)], body=1.6,
                          rate=44, rasp=0.75, room=(1.4, 0.16)), "Raptorsound3"),
    "troodon": (prof(scream=[g(HERON, 0.9), g(PEL, 1.0)], growl=[g(BEAR2, 1.4)], body=1.2, rate=55, room=(1.2, 0.15),
                     g=dict(hiss=0.3)), "Troodonsound"),
    "compsognathus": (prof(scream=[g(HERON2, 1.15), g(PEL, 1.2)], growl=[g(BEAR2, 1.6)], body=0.8, rate=60, room=(0.9, 0.12)),
                      "Microraptorsound"),
    "mononykus": (prof(scream=[g(HERON, 1.1)], growl=[g(BEAR2, 1.5)], body=0.8, rate=60, room=(0.9, 0.12)), "Microraptorsound"),
    "didelphodon": (prof(scream=[g(PEL, 0.6)], growl=[g(BEAR1, 0.9), g(GW_LO, 1.0)], body=1.2, rate=45, room=(1.0, 0.14),
                         g=dict(scream=0.3, hiss=0.8)), "Purloviasound"),
    # aves corredoras e terizinossauros
    "oviraptor": (prof(k=1.1, scream=[g(PEL, 0.8), g(CRANE, 1.0)], growl=[g(BISB, 1.4)], body=1.2, room=(1.2, 0.15)), "Gallimimus_Roar_1"),
    "citipati": (prof(scream=[g(CRANE, 0.7)], growl=[g(BEAR1, 0.9)], low=[g(BISB, 1.1)], body=1.4, room=(1.3, 0.16)),
                 "Ark_Terrorbrid_Attack_Bite_1"),
    "gallimimus": (prof(scream=[g(PEL, 0.8), g(CRANE, 1.0)], growl=[g(BISB, 1.4)], body=1.3, room=(1.3, 0.16)), "Gallimimus_Roar_1"),
    "struthiomimus": (prof(k=1.05, scream=[g(PEL, 0.8), g(CRANE2, 1.0)], growl=[g(BISB, 1.4)], body=1.3, room=(1.3, 0.16)),
                      "Gallimimus_Roar_1"),
    "therizinosaurus": (prof(scream=[g(CRANE, 0.45)], growl=[g(BISB2, 0.8), g(BEAR1, 0.7)], low=[g(ALLI, 0.95)], body=2.2,
                             g=dict(rumble=0.5)), "Therizinosound"),
    "deinocheirus": (prof(k=0.9, scream=[g(CRANE3, 0.45)], growl=[g(BISB2, 0.8), g(BEAR2, 0.7)], low=[g(ALLI, 0.95)], body=2.4,
                          g=dict(rumble=0.6)), "Therizinosound"),
    # hadrossauros: trompa (elk bem lento vira uma trompa grave)
    "parasaurolophus": (prof(scream=[g(ELK2, 0.24), g(CRANE2, 0.5)], growl=[g(BISB, 0.9)], low=[g(ALLI, 0.9)], body=2.6,
                             rasp=0.25, g=dict(scream=0.9, air=0.6, rumble=0.4)), "Parasaursound"),
    "corythosaurus": (prof(k=1.1, scream=[g(ELK, 0.24), g(CRANE3, 0.5)], growl=[g(BISB, 0.9)], low=[g(ALLI, 0.9)], body=2.4,
                           rasp=0.25, g=dict(scream=0.9, air=0.6, rumble=0.4)), "Parasaursound"),
    "edmontosaurus": (prof(k=0.9, scream=[g(CRANE, 0.5)], growl=[g(BISA, 0.7), g(BISB, 0.8)], low=[g(ALLI2, 0.8)], body=2.2,
                           g=dict(rumble=0.6)), "Iguanodon_sound"),
    "maiasaura": (prof(scream=[g(CRANE2, 0.5)], growl=[g(BISA, 0.7), g(BISB, 0.8)], low=[g(ALLI2, 0.8)], body=2.0,
                       g=dict(rumble=0.5)), "Iguanodon_sound"),
    "pachycephalosaurus": (prof(scream=[g(CRANE3, 0.5)], growl=[g(("bisb", 2), 0.9), g(BEAR1, 0.8)], body=1.1,
                                g=dict(scream=0.3, rumble=0.3)), "Pachysound"),
    "thescelosaurus": (prof(scream=[g(("heron", 2), 1.0)], growl=[g(BEAR2, 1.3)], body=0.8, rate=55, room=(1.0, 0.12)),
                       "Pegomastaxsound"),
    # ceratopsianos e encouraçados
    "triceratops": (prof(k=0.9, scream=[g(CRANE3, 0.45)], growl=[g(ALLI2, 0.85), g(BISA, 0.6)], low=[g(ALLI, 0.9)], body=2.0,
                         g=dict(scream=0.3, rumble=0.6)), "S_pachyrhino_idle_02"),
    "styracosaurus": (prof(k=1.05, scream=[g(CRANE3, 0.45)], growl=[g(ALLI2, 0.85), g(BISA, 0.6)], low=[g(ALLI, 0.9)], body=1.8,
                           g=dict(scream=0.3, rumble=0.5)), "Pachysound"),
    "pachyrhinosaurus": (prof(scream=[g(CRANE3, 0.45)], growl=[g(ALLI2, 0.85), g(BISA, 0.6)], low=[g(ALLI_B, 0.9)], body=1.9,
                              g=dict(scream=0.3, rumble=0.5)), "S_pachyrhino_idle_02"),
    "protoceratops": (prof(k=1.0, scream=[g(("heron", 2), 0.95)], growl=[g(BEAR2, 1.3)], body=0.8, rate=55, room=(1.0, 0.12)),
                      "Pegomastaxsound"),
    "ankylosaurus": (prof(scream=[g(CRANE, 0.5)], growl=[g(BISB2, 0.75), g(ALLI, 0.9)], low=[g(ALLI2, 0.85)], body=1.6,
                          g=dict(scream=0.35, rumble=0.7)), "Ankylosound"),
    "euoplocephalus": (prof(k=1.08, scream=[g(CRANE2, 0.5)], growl=[g(BISB2, 0.75), g(ALLI, 0.9)], low=[g(ALLI2, 0.85)], body=1.5,
                            g=dict(scream=0.35, rumble=0.6)), "Ankylosound"),
    "stegosaurus": (prof(scream=[g(ELK, 0.3)], growl=[g(ALLI2, 0.8), g(BISA, 0.6)], low=[g(ALLI, 0.85)], body=1.8,
                         g=dict(scream=0.35, rumble=0.5)), "Stegosound"),
    # saurópodes: gemido grave de baleia (elk muito lento) sobre bramido e grave profundo
    "brachiosaurus": (prof(scream=[g(ELK2, 0.2)], growl=[g(ALLI2, 0.55), g(BISA, 0.45)], low=[g(ALLI, 0.6)], body=3.6, rasp=0.4,
                           room=(2.6, 0.26), g=dict(scream=0.6, rumble=1.4, air=0.6)), "Brontosound"),
    "alamosaurus": (prof(scream=[g(ELK, 0.22)], growl=[g(ALLI2, 0.6), g(BISB, 0.5)], low=[g(ALLI, 0.65)], body=3.2, rasp=0.4,
                         room=(2.4, 0.24), g=dict(scream=0.6, rumble=1.0, air=0.7)), "Titanosaursound"),
    "saltasaurus": (prof(k=1.15, scream=[g(ELK2, 0.22)], growl=[g(ALLI2, 0.6), g(BISB, 0.5)], low=[g(ALLI, 0.65)], body=2.6,
                         rasp=0.4, room=(2.2, 0.22), g=dict(scream=0.6, rumble=0.8, air=0.7)), "Diplodocussound"),
    "argentinosaurus": (prof(k=0.9, scream=[g(ELK2, 0.2)], growl=[g(ALLI2, 0.55), g(BISA, 0.45)], low=[g(ALLI, 0.6)], body=4.0,
                             rasp=0.4, room=(2.8, 0.28), g=dict(scream=0.6, rumble=1.4, air=0.6)), "Titanosaursound"),
    "opisthocoelicaudia": (prof(k=1.1, scream=[g(ELK, 0.24)], growl=[g(ALLI_B, 0.65), g(BISB, 0.55)], low=[g(ALLI2, 0.7)],
                                body=2.8, rasp=0.4, room=(2.2, 0.22), g=dict(scream=0.6, rumble=0.8, air=0.7)), "Amargasound"),
    "dreadnoughtus": (prof(k=0.95, scream=[g(ELK, 0.2)], growl=[g(ALLI2, 0.55), g(BISB, 0.45)], low=[g(ALLI, 0.6)], body=3.8,
                           rasp=0.4, room=(2.6, 0.26), g=dict(scream=0.6, rumble=1.2, air=0.6)), "Titanosaursound"),
    # pterossauros e aves
    "pteranodon": (prof(scream=[g(CRANE, 0.85), g(PEL, 0.6)], growl=[g(BEAR2, 1.0)], body=1.5, room=(1.6, 0.2)), "Pteranodonsound"),
    "quetzalcoatlus": (prof(scream=[g(CRANE2, 0.55), g(PEL, 0.45)], growl=[g(BEAR1, 0.7)], body=2.2, room=(2.0, 0.22),
                            g=dict(rumble=0.3)), "Quetzalsound"),
    "hatzegopteryx": (prof(k=0.95, scream=[g(CRANE3, 0.55), g(PEL, 0.45)], growl=[g(BEAR1, 0.65)], body=2.2, room=(2.0, 0.22),
                           g=dict(rumble=0.4)), "Quetzalsound"),
    "ichthyornis": (prof(scream=[g(HERON2, 1.0), g(PEL, 1.0)], growl=[g(BEAR2, 1.5)], body=1.0, room=(1.4, 0.18)), "Icthyornissound"),
    "hesperornis": (prof(scream=[g(CRANE2, 1.1), g(ELK2, 0.6)], growl=[g(BEAR2, 1.2)], body=1.4, rasp=0.35, room=(1.6, 0.2)),
                    "Hespererornissound"),
    # marinhos e crocodilos
    "mosasaurus": (prof(k=0.9, scream=[g(ELK2, 0.2)], growl=[g(ALLI2, 0.7)], low=[g(ALLI, 0.7)], body=2.6, rasp=0.5,
                        room=(2.4, 0.3), g=dict(scream=0.6, rumble=0.9, air=1.3)), "Basilosound"),
    "tylosaurus": (prof(scream=[g(ELK, 0.22)], growl=[g(ALLI2, 0.75)], low=[g(ALLI, 0.75)], body=2.4, rasp=0.5,
                        room=(2.2, 0.28), g=dict(scream=0.6, rumble=0.8, air=1.3)), "Basilosound"),
    "elasmosaurus": (prof(scream=[g(ELK, 0.22)], growl=[g(ALLI2, 0.7)], low=[g(ALLI_B, 0.75)], body=2.2, rasp=0.3,
                          room=(2.4, 0.3), g=dict(scream=0.7, rumble=0.6, air=0.6)), "Lioplurodonsound"),
    "archelon": (prof(scream=[g(PEL, 0.5)], growl=[g(BISA, 1.0)], low=[g(("alli", 0), 1.0)], body=1.2, room=(1.4, 0.18),
                      g=dict(scream=0.25, hiss=0.9)), "Carbonemyssound"),
    "xiphactinus": (prof(scream=[], growl=[g(ALLI, 0.8), g(ALLI2, 0.9)], body=1.8, rasp=0.8, rate=20, room=(1.8, 0.25),
                         g=dict(rumble=0.5, air=0.7)), "Leedsichtyssound"),
    "deinosuchus": (prof(k=0.85, scream=[g(PEL, 0.6)], growl=[g(ALLI, 0.9), g(ALLI2, 0.85)], body=2.2, rate=30,
                         g=dict(scream=0.4, hiss=0.8, rumble=0.5)), "Kaprosuchus_sound"),
    "baurusuchus": (prof(scream=[g(PEL, 0.6)], growl=[g(ALLI, 0.9), g(ALLI2, 0.85)], body=1.8, rate=32,
                         g=dict(scream=0.4, hiss=0.8, rumble=0.3)), "Kaprosuchus_sound"),
}

# ajuste de cada espécie às medidas do ARK (ajustar.py, só números)
KNOBS = {
    "tyrannosaurus": dict(km=0.94, sm=1.4, am=1.5, gm=0.4),
    "tarbosaurus": dict(km=0.94, sm=0.6, am=1.5, gm=0.4),
    "daspletosaurus": dict(km=1.07, sm=0.6, am=1.0, gm=0.4),
    "albertosaurus": dict(km=0.94, sm=1.4, am=1.5, gm=0.8),
    "carnotaurus": dict(km=1.07, sm=0.6, am=1.5, gm=0.4),
    "giganotosaurus": dict(km=1.07, sm=1.4, am=1.5, gm=0.4),
    "spinosaurus": dict(km=0.94, sm=0.6, am=1.5, gm=0.8),
    "carcharodontosaurus": dict(km=1.07, sm=0.6, am=1.5, gm=0.4),
    "dilophosaurus": dict(km=1.0, sm=1.4, am=0.6, gm=0.4),
    "majungasaurus": dict(km=1.07, sm=0.6, am=0.6, gm=0.4),
    "dakotaraptor": dict(km=0.94, sm=0.6, am=1.5, gm=0.4),
    "velociraptor": dict(km=1.0, sm=0.6, am=1.5, gm=0.4),
    "compsognathus": dict(km=0.94, sm=1.4, am=1.0, gm=0.4),
    "troodon": dict(km=1.07, sm=1.4, am=1.0, gm=0.4),
    "mononykus": dict(km=0.94, sm=1.4, am=0.6, gm=0.4),
    "didelphodon": dict(km=0.94, sm=0.6, am=0.6, gm=0.8),
    "oviraptor": dict(km=1.07, sm=1.4, am=0.6, gm=0.4),
    "gallimimus": dict(km=1.0, sm=1.4, am=1.5, gm=0.4),
    "struthiomimus": dict(km=1.07, sm=1.4, am=0.6, gm=0.4),
    "citipati": dict(km=0.94, sm=0.6, am=1.5, gm=0.4),
    "therizinosaurus": dict(km=1.07, sm=0.6, am=0.6, gm=0.4),
    "deinocheirus": dict(km=1.07, sm=0.6, am=1.0, gm=0.4),
    "parasaurolophus": dict(km=1.0, sm=0.6, am=1.0, gm=0.8),
    "corythosaurus": dict(km=0.94, sm=0.6, am=1.5, gm=0.4),
    "pachycephalosaurus": dict(km=0.94, sm=0.6, am=0.6, gm=0.4),
    "edmontosaurus": dict(km=0.94, sm=0.6, am=0.6, gm=0.4),
    "thescelosaurus": dict(km=1.07, sm=1.4, am=0.6, gm=0.4),
    "maiasaura": dict(km=1.0, sm=0.6, am=0.6, gm=0.4),
    "protoceratops": dict(km=1.07, sm=1.4, am=0.6, gm=0.4),
    "triceratops": dict(km=1.07, sm=0.6, am=0.6, gm=0.4),
    "styracosaurus": dict(km=1.07, sm=1.4, am=1.0, gm=0.4),
    "ankylosaurus": dict(km=1.0, sm=0.6, am=1.5, gm=0.4),
    "pachyrhinosaurus": dict(km=1.07, sm=0.6, am=0.6, gm=0.4),
    "euoplocephalus": dict(km=1.0, sm=0.6, am=1.5, gm=0.4),
    "stegosaurus": dict(km=0.94, sm=0.6, am=0.6, gm=0.8),
    "alamosaurus": dict(km=1.07, sm=1.4, am=1.5, gm=0.8),
    "brachiosaurus": dict(km=0.94, sm=0.6, am=1.5, gm=0.4),
    "saltasaurus": dict(km=1.0, sm=1.4, am=0.6, gm=0.8),
    "opisthocoelicaudia": dict(km=1.0, sm=1.4, am=1.5, gm=0.8),
    "argentinosaurus": dict(km=1.07, sm=1.4, am=1.5, gm=0.8),
    "pteranodon": dict(km=1.07, sm=1.4, am=1.5, gm=0.8),
    "quetzalcoatlus": dict(km=1.07, sm=0.6, am=0.6, gm=0.4),
    "ichthyornis": dict(km=0.94, sm=1.4, am=0.6, gm=0.4),
    "hatzegopteryx": dict(km=1.07, sm=0.6, am=1.0, gm=0.4),
    "dreadnoughtus": dict(km=1.0, sm=1.4, am=1.5, gm=0.8),
    "hesperornis": dict(km=1.07, sm=1.4, am=1.0, gm=0.4),
    "tylosaurus": dict(km=1.07, sm=1.4, am=1.0, gm=0.4),
    "elasmosaurus": dict(km=0.94, sm=0.6, am=1.5, gm=0.8),
    "archelon": dict(km=1.0, sm=0.6, am=1.5, gm=0.4),
    "mosasaurus": dict(km=0.94, sm=0.6, am=1.5, gm=0.8),
    "xiphactinus": dict(km=1.07, sm=0.6, am=1.0, gm=0.8),
    "deinosuchus": dict(km=1.0, sm=0.6, am=0.6, gm=0.4),
    "baurusuchus": dict(km=1.0, sm=1.4, am=0.6, gm=0.4),
}


def variant(p, km, sm, am, gm):
    import copy
    q = copy.deepcopy(p); q["k"] *= km
    q["g"]["scream"] *= sm; q["g"]["air"] *= am; q["g"]["growl"] *= gm; q["g"]["low"] *= gm
    return q


def cut(name, a, b, speed=1.0, fi=0.02, fo=0.3):
    """trecho a..b s de uma gravação, desacelerado por reamostragem, sem pulsar regular"""
    x = load(name)[int(a * SR):int(b * SR)]
    if speed != 1.0:
        m = int(len(x) / speed); x = np.interp(np.linspace(0, len(x) - 1, m), np.arange(len(x)), x)
    x = alisar(alisar(x - np.mean(x)))
    return norm(x * envelope(len(x), fi, fo * len(x) / SR, 1.0), 1.0)


def rex_e(seed=4):
    """o rugido do T. rex que o Rodrigo escolheu (versão E, 2026-10-31; sem o pulsar de moto, 2026-11-01):
    ronco de jacaré subindo, urso, alce desacelerado, bisão, ar de garganta e grave"""
    body, intro, rasp = 4.0, 0.8, 0.7
    rng = np.random.default_rng(seed)
    pre = denoise(cut("alli", 1.3, 2.3, speed=0.85, fi=0.4, fo=0.15))
    griz = denoise(cut("griz", 9.1, 9.1 + body * 1.0 + 0.6, speed=1.0, fi=0.04, fo=0.5))
    elk = denoise(cut("elk", 8.4, 8.4 + body * 0.42, speed=0.42, fi=0.12, fo=0.5))
    eh = denoise(cut("elk", 12.6, 12.6 + body * 0.8, speed=0.8, fi=0.2, fo=0.5))
    bis = denoise(cut("bisa", 1.55, 2.8, speed=0.75, fi=0.005, fo=0.5))
    voice = place([(intro - 0.05, bis, 0.5), (intro, griz, 0.8), (intro + 0.1, elk, 0.7), (intro + 0.2, eh, 0.1)])
    n = len(voice) + int(0.4 * SR); voice = np.concatenate([voice, np.zeros(n - len(voice))])
    env = smooth(np.abs(voice), int(SR * 0.04)); env /= env.max() + 1e-9
    air = noise(n, rng, 0.4) * ((1 - rasp) + rasp * aspero(n, 38, rng))
    air = spectral_filter(air, ((520, 450, 0), (1250, 800, -2), (2600, 1400, -6), (4200, 1800, -10)), floor=0.02)
    air = norm(air * env ** 1.3, 1.0)
    rr = np.random.default_rng(seed)
    rm = norm(spectral_filter(noise(n, rr, 2.0), (), floor=1.0, hp=22, lp=85) * envelope(n, 0.6, 1.5, 1.0), 1.0)
    x = place([(0.0, pre, 0.7), (0.0, voice, 1.0), (0.0, air, 1.0), (0.0, rm, 0.9)])
    x = alisar(x, amount=0.7)
    x = spectral_filter(x, (), floor=1.0, hp=22, lp=9500); x = drive(x, 3.0); x = reverb(x, 2.2, 0.22)
    return norm(x, 0.9)


EVENT_FN = {"ambient": ambient, "threat": threat, "hurt": hurt, "death": death}


def render(sid, event, v=0):
    """a voz `event` (variação v) da espécie sid, em amostras float a SR"""
    if sid == "tyrannosaurus" and event == "threat" and v == 0:
        return rex_e()
    p, _ = P[sid]
    return EVENT_FN[event](variant(p, **KNOBS[sid]), v)
