"""Compile and run the production spawn-budget tests in a temporary directory, using JDK 21."""
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    with tempfile.TemporaryDirectory(prefix="terrassic-budget-") as directory:
        subprocess.run([
            "javac", "--release", "17", "-d", directory,
            str(ROOT / "common/src/main/java/com/terrassic/world/SpawnBudget.java"),
            str(ROOT / "tools/validation/java/SpawnBudgetTest.java"),
        ], check=True)
        subprocess.run(["java", "-cp", directory, "com.terrassic.world.SpawnBudgetTest"], check=True)


if __name__ == "__main__":
    main()
