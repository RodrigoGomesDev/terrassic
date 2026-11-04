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

    def test_embed_lista_os_commits_com_cor_e_link_de_comparacao(self):
        commit(self.repo, "1.0.0", "1.0.0: número da versão")
        commit(self.repo, "1.0.0", "Tricerátopo: revisão 1.5")
        commit(self.repo, "1.1.0", "1.1.0: número da versão")
        since_sha, _ = ab.find_previous_bump(ab.bump_commits(), "1.1.0")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        embed = ab.build_embed("1.1.0", ab.changelog(since_sha), since_sha, head)
        self.assertEqual(embed["color"], ab.COLOR)
        self.assertIn("1.1.0", embed["title"])
        self.assertIn("Tricerátopo: revisão 1.5", embed["description"])
        self.assertIn(since_sha[:12], embed["url"])
        self.assertIn(head[:12], embed["url"])

    def test_mais_de_12_commits_resume_com_contagem(self):
        commit(self.repo, "1.0.0", "1.0.0: número da versão")
        for n in range(15):
            commit(self.repo, "1.0.0", f"Ajuste {n}")
        commit(self.repo, "1.1.0", "1.1.0: número da versão")
        since_sha, _ = ab.find_previous_bump(ab.bump_commits(), "1.1.0")
        embed = ab.build_embed("1.1.0", ab.changelog(since_sha), since_sha, "x" * 40)
        self.assertIn("…and 3 more commit(s).", embed["description"])

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
