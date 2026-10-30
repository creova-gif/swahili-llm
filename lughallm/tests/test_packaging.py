"""
Regression test: the SWAHILI-BENCH dataset must be shipped inside the built
wheel, otherwise `lughallm bench` raises FileNotFoundError after `pip install .`.
Compatible with standard library unittest and pytest.
"""

import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_IN_WHEEL = "lughallm/src/benchmark/dataset.json"


class TestPackaging(unittest.TestCase):

    def test_dataset_exists_next_to_bench_module(self):
        from lughallm.src.benchmark import swahili_bench
        path = os.path.join(os.path.dirname(swahili_bench.__file__), "dataset.json")
        self.assertTrue(os.path.isfile(path), f"missing {path}")

    def test_wheel_includes_benchmark_dataset(self):
        try:
            import pip  # noqa: F401
        except ImportError:
            self.skipTest("pip is not available to build a wheel")
        with tempfile.TemporaryDirectory() as out:
            proc = subprocess.run(
                [sys.executable, "-m", "pip", "wheel", "--no-deps", "--quiet",
                 "--wheel-dir", out, REPO_ROOT],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            wheels = [f for f in os.listdir(out) if f.endswith(".whl")]
            self.assertEqual(len(wheels), 1, wheels)
            with zipfile.ZipFile(os.path.join(out, wheels[0])) as whl:
                self.assertIn(DATASET_IN_WHEEL, whl.namelist())


if __name__ == "__main__":
    unittest.main()
