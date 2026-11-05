"""Avisa no Discord quando mod_version muda em gradle.properties, com o changelog desde o aviso anterior.
O servidor do Discord é organizado em inglês: a moldura do aviso é em inglês; o changelog são os assuntos dos commits.

Rodado pelo GitHub Actions (.github/workflows/discord-build.yml) a cada push em main que toca gradle.properties.
É o canal de BUILDS: toda vez que a versão muda, mesmo sem tag git. O aviso OFICIAL de lançamento
("Terrassic vX.Y.Z saiu!", no canal de avisos) continua sendo o Rexpert, vigiando as tags vX.Y.Z (ver
rexpert/src/lib/releases.js) — tagueie a versão quando quiser esse anúncio maior.

Sem DISCORD_BUILDS_WEBHOOK (fork, PR, rodando à mão sem configurar), só mostra o que seria enviado e sai sem erro:
nunca falha a build de ninguém por causa de um aviso.

Rodar à mão: python3 -B tools/discord/announce_build.py
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = "RodrigoGomesDev/terrassic"
COLOR = 0xF07A1A  # laranja da Fenda, o mesmo do site e do Rexpert
MAX_COMMITS = 12

# Mensagens só com o número da versão, sem descrever nada: "1.5.0: número da versão", "Versão 1.0.0", "v1.0.0".
GENERIC_BUMP = re.compile(r"^(v|versão\s+)?\d+\.\d+\.\d+(:\s*número da versão)?$", re.IGNORECASE)


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def version_at(ref):
    """mod_version de gradle.properties num commit. None se o arquivo não existir ali ou não tiver a chave."""
    try:
        text = git("show", f"{ref}:gradle.properties")
    except subprocess.CalledProcessError:
        return None
    m = re.search(r"^mod_version\s*=\s*(\S+)", text, re.MULTILINE)
    return m.group(1) if m else None


def bump_commits():
    """Commits que tocaram gradle.properties, do mais novo (HEAD) para o mais antigo."""
    out = git("log", "--format=%H", "--", "gradle.properties")
    return [line for line in out.splitlines() if line]


def find_previous_bump(commits, current_version):
    """O commit que introduziu a versão anterior (a última diferente da atual), e qual era ela.

    `commits` é a lista de bump_commits() (mais novo primeiro). Precisa andar até o início da leva de
    commits com a versão anterior — não o mais próximo do HEAD — para o changelog não repetir o que já
    foi avisado da vez passada. Sem versão anterior (primeira vez, ou a versão nunca mudou): (None, None).
    """
    idx = None
    previous_version = None
    for i, sha in enumerate(commits[1:], start=1):
        v = version_at(sha)
        if v is not None and v != current_version:
            idx = i
            previous_version = v
            break
    if idx is None:
        return None, None
    since_idx = idx
    for j in range(idx + 1, len(commits)):
        if version_at(commits[j]) != previous_version:
            break
        since_idx = j
    return commits[since_idx], previous_version


def changelog(since_sha):
    """Mensagens (sem merges) de since_sha (exclusive) até HEAD, sem as genéricas de "número da versão"."""
    out = git("log", "--format=%s", "--no-merges", f"{since_sha}..HEAD")
    subjects = [s for s in out.splitlines() if s.strip() and not GENERIC_BUMP.match(s.strip())]
    return subjects


def build_embed(version, subjects, since_sha, head_sha):
    shown = subjects[:MAX_COMMITS]
    extra = len(subjects) - len(shown)
    lines = [f"• {s}" for s in shown] or ["No described commits since the last announcement."]
    if extra > 0:
        lines.append(f"…and {extra} more commit(s).")
    embed = {
        "title": f"🦖 Terrassic {version} · new build",
        "description": "\n".join(lines),
        "color": COLOR,
        "footer": {"text": "Automatic build on every new version — not the official release."},
    }
    if since_sha:
        embed["url"] = f"https://github.com/{REPO}/compare/{since_sha[:12]}...{head_sha[:12]}"
    return embed


def send(webhook, embed):
    body = json.dumps({"embeds": [embed]}).encode("utf-8")
    # Discord (Cloudflare) answers 403 to the default "Python-urllib" agent: a bot names itself, in Discord's format
    headers = {"Content-Type": "application/json", "User-Agent": f"DiscordBot (https://github.com/{REPO}, 1.0)"}
    req = urllib.request.Request(webhook, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.status


def main():
    webhook = os.environ.get("DISCORD_BUILDS_WEBHOOK", "").strip()
    current = version_at("HEAD")
    if not current:
        print("gradle.properties sem mod_version; nada a avisar.")
        return 0

    commits = bump_commits()
    since_sha, previous = (None, None) if len(commits) <= 1 else find_previous_bump(commits, current)
    if len(commits) > 1 and previous is None:
        print(f"Não achei uma versão anterior diferente de {current} na história; nada a avisar.")
        return 0
    if previous == current:
        print(f"Versão ainda é {current}; nada a avisar.")
        return 0

    head_sha = git("rev-parse", "HEAD").strip()
    subjects = changelog(since_sha) if since_sha else []
    print(f"Nova versão: {current} (antes: {previous or 'nenhuma — primeira registrada'}). {len(subjects)} commit(s).")
    embed = build_embed(current, subjects, since_sha, head_sha)

    if not webhook:
        print("DISCORD_BUILDS_WEBHOOK não configurado: mostrando o que seria enviado, sem enviar.")
        print(json.dumps(embed, ensure_ascii=False, indent=2))
        return 0

    try:
        status = send(webhook, embed)
        print(f"Discord: HTTP {status}")
    except Exception as err:  # um aviso falhando não pode quebrar o pipeline de ninguém
        print(f"Falha ao avisar no Discord: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
