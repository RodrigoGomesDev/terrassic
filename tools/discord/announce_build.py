"""Avisa no Discord quando mod_version muda em gradle.properties, com as notas da versão EM INGLÊS.

O servidor do Discord é organizado em inglês. O texto do aviso vem da seção "## English" de
docs/changelog/X.Y.Z.md (o mesmo changelog que vai para as lojas, docs/VERSOES.md). Os assuntos dos commits não vão
mais para o Discord: são em português e falam a língua da equipe, não a do jogador. Versão sem changelog no
repositório: o aviso sai só com "build nova" e o link das mudanças, e o log da Action avisa que faltou o arquivo.

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
MAX_DESCRIPTION = 3900  # o limite do Discord é 4096; sobra espaço para o "notas completas"

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


def notes_path(version):
    return ROOT / "docs" / "changelog" / f"{version}.md"


def english_notes(version):
    """A seção "## English" de docs/changelog/<versão>.md, pronta para o Discord, ou None se não houver.

    Títulos "###" viram negrito (o embed não mostra título de markdown); o resto (listas, negrito) o Discord já mostra.
    """
    path = notes_path(version)
    if not path.exists():
        return None
    m = re.search(r"^##\s+English\s*$(.*?)(?=^##\s|\Z)", path.read_text(encoding="utf-8"), re.MULTILINE | re.DOTALL)
    if not m:
        return None
    lines = []
    for line in m.group(1).strip().splitlines():
        line = re.sub(r"^#{3,}\s+(.*)$", r"**\1**", line.rstrip())
        # Linha quebrada no meio da frase (continuação recuada, sem "- "): o Discord mostra cada quebra, então junta.
        if lines and lines[-1] and re.match(r"^\s+(?![-*]\s)\S", line):
            lines[-1] += " " + line.strip()
        else:
            lines.append(line)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return text or None


def fit(text, more_url):
    """Corta nas quebras de linha para caber no embed, com o link das notas completas no fim."""
    if len(text) <= MAX_DESCRIPTION:
        return text
    cut = text[:MAX_DESCRIPTION].rsplit("\n", 1)[0].rstrip()
    return f"{cut}\n…\n[Full patch notes]({more_url})"


def build_embed(version, notes, since_sha, head_sha):
    full = f"https://github.com/{REPO}/blob/main/docs/changelog/{version}.md"
    description = fit(notes, full) if notes else "A new build is out. Patch notes come with the release."
    embed = {
        "title": f"🦖 Terrassic {version} · new build",
        "description": description,
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
    notes = english_notes(current)
    print(f"Nova versão: {current} (antes: {previous or 'nenhuma — primeira registrada'}). {len(subjects)} commit(s).")
    if not notes:
        print(f"Sem a seção '## English' em {notes_path(current).relative_to(ROOT)}: o aviso sai sem as notas (docs/VERSOES.md).")
    embed = build_embed(current, notes, since_sha, head_sha)

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
