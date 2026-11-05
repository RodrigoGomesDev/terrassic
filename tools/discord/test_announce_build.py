"""Testes de announce_build.py com um repositório git de mentira: sem rede, sem tocar no Terrassic de verdade.

Rodar: python3 -B -m unittest discover -s tools/discord -p 'test_*.py'
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import announce_build as ab  # noqa: E402


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout


_counter = [0]


def commit(repo, version, message):
    # O contador garante que o arquivo sempre muda, mesmo quando dois commits seguidos têm a mesma versão
    # (caso real: um ajuste qualquer em gradle.properties sem mexer no mod_version).
    _counter[0] += 1
    (repo / "gradle.properties").write_text(f"mod_version = {version}\nbuild_counter = {_counter[0]}\n")
    git(repo, "add", "gradle.properties")
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", message)


class TestAnnounceBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q", "-b", "main")
        self.addCleanup(self.tmp.cleanup)
        self._root = ab.ROOT
        ab.ROOT = self.repo  # roda o script dentro do repositório de teste, não no Terrassic de verdade
        self.addCleanup(lambda: setattr(ab, "ROOT", self._root))

    def test_acha_a_versao_anterior_e_o_changelog_so_do_que_ainda_nao_foi_avisado(self):
        commit(self.repo, "1.0.0", "1.0.0: número da versão")
        commit(self.repo, "1.0.0", "Tricerátopo: revisão 1.5")
        commit(self.repo, "1.0.0", "Anquilossauro: revisão 1.5")
        commit(self.repo, "1.1.0", "1.1.0: número da versão")
        current = ab.version_at("HEAD")
        self.assertEqual(current, "1.1.0")

        since_sha, previous = ab.find_previous_bump(ab.bump_commits(), current)
        self.assertEqual(previous, "1.0.0")
        # A própria linha "1.1.0: número da versão" não entra: o título do aviso já diz a versão.
        self.assertEqual(ab.changelog(since_sha), ["Anquilossauro: revisão 1.5", "Tricerátopo: revisão 1.5"])

    def test_mensagem_generica_de_bump_nao_aparece_no_changelog(self):
        commit(self.repo, "1.0.0", "1.0.0: número da versão")
        commit(self.repo, "1.1.0", "1.1.0: número da versão")
        since_sha, _ = ab.find_previous_bump(ab.bump_commits(), ab.version_at("HEAD"))
        self.assertEqual(ab.changelog(since_sha), [])

    def test_sem_mudanca_de_versao_nada_para_avisar(self):
        commit(self.repo, "1.0.0", "1.0.0: número da versão")
        commit(self.repo, "1.0.0", "ajuste que não mexe na versão")
        since_sha, previous = ab.find_previous_bump(ab.bump_commits(), ab.version_at("HEAD"))
        self.assertIsNone(since_sha)
        self.assertIsNone(previous)

    def test_trabalho_antes_da_versao_anterior_fica_de_fora(self):
        # Era 0.9.0 (não deve aparecer no changelog da 1.1.0: já foi avisada na época).
        commit(self.repo, "0.9.0", "0.9.0: número da versão")
        commit(self.repo, "0.9.0", "Espinossauro: nado novo")
        commit(self.repo, "1.0.0", "1.0.0: número da versão")
        commit(self.repo, "1.0.0", "Tricerátopo: revisão 1.5")
        commit(self.repo, "1.1.0", "1.1.0: número da versão")
        since_sha, previous = ab.find_previous_bump(ab.bump_commits(), ab.version_at("HEAD"))
        self.assertEqual(previous, "1.0.0")
        log = ab.changelog(since_sha)
        self.assertIn("Tricerátopo: revisão 1.5", log)
        self.assertNotIn("Espinossauro: nado novo", log)

    def notes(self, version, text):
        path = self.repo / "docs" / "changelog" / f"{version}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_embed_usa_a_secao_em_ingles_do_changelog_e_nunca_os_commits(self):
        commit(self.repo, "1.0.0", "1.0.0: número da versão")
        commit(self.repo, "1.0.0", "Tricerátopo: revisão 1.5")
        commit(self.repo, "1.1.0", "1.1.0: número da versão")
        self.notes("1.1.0", "# Terrassic 1.1.0\n\n## Português\n\n### Tricerátopo\n- Modelo novo.\n\n"
                            "## English\n\n### Triceratops\n- New model.\n  - with a frill\n")
        since_sha, _ = ab.find_previous_bump(ab.bump_commits(), "1.1.0")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        embed = ab.build_embed("1.1.0", ab.english_notes("1.1.0"), since_sha, head)
        self.assertEqual(embed["color"], ab.COLOR)
        self.assertIn("1.1.0", embed["title"])
        self.assertEqual(embed["description"], "**Triceratops**\n- New model.\n  - with a frill")
        self.assertNotIn("Tricerátopo", embed["description"])
        self.assertIn(since_sha[:12], embed["url"])
        self.assertIn(head[:12], embed["url"])

    def test_sem_changelog_o_aviso_sai_em_ingles_sem_os_commits(self):
        commit(self.repo, "1.0.0", "1.0.0: número da versão")
        commit(self.repo, "1.0.0", "Tricerátopo: revisão 1.5")
        commit(self.repo, "1.1.0", "1.1.0: número da versão")
        self.assertIsNone(ab.english_notes("1.1.0"))
        self.notes("1.1.0", "# Terrassic 1.1.0\n\n## Português\n- só português\n")
        self.assertIsNone(ab.english_notes("1.1.0"), "sem a seção English, nada")
        embed = ab.build_embed("1.1.0", None, None, "x" * 40)
        self.assertEqual(embed["description"], "A new build is out. Patch notes come with the release.")

    def test_linha_quebrada_no_meio_da_frase_vira_uma_so(self):
        self.notes("1.2.0", "## English\n\n- Dinos are hit where you see them, with boxes that\n  follow the model.\n  - a real sub-item\n")
        self.assertEqual(ab.english_notes("1.2.0"), "- Dinos are hit where you see them, with boxes that follow the model.\n  - a real sub-item")

    def test_notas_longas_cortam_na_linha_com_link_para_as_completas(self):
        long = "\n".join(f"- change number {n} with some words" for n in range(300))
        out = ab.fit(long, "https://example.com/full")
        self.assertLessEqual(len(out), 4096)
        self.assertTrue(out.endswith("[Full patch notes](https://example.com/full)"))
        self.assertIn("\n…\n", out)

    def test_primeira_versao_sem_webhook_nao_falha(self):
        commit(self.repo, "0.1.0", "0.1.0: primeira versão")
        self.assertEqual(ab.bump_commits(), [git(self.repo, "rev-parse", "HEAD").strip()])
        os_environ_backup = ab.os.environ.pop("DISCORD_BUILDS_WEBHOOK", None)
        try:
            self.assertEqual(ab.main(), 0)
        finally:
            if os_environ_backup is not None:
                ab.os.environ["DISCORD_BUILDS_WEBHOOK"] = os_environ_backup

    def test_gradle_properties_sem_mod_version_nao_quebra(self):
        (self.repo / "gradle.properties").write_text("loom_version = 1.17\n")
        git(self.repo, "add", "gradle.properties")
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "sem versão")
        self.assertIsNone(ab.version_at("HEAD"))
        self.assertEqual(ab.main(), 0)


if __name__ == "__main__":
    unittest.main()
