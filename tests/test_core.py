import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from local_dev_launcher.core import ConfigError, Launcher, load_config


class ConfigTests(unittest.TestCase):
    def test_loads_valid_config(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "dev-launch.json"
            path.write_text(json.dumps({"processes": [{"name": "api", "command": [sys.executable, "-V"], "env": {"MODE": "dev"}}]}), encoding="utf-8")
            specs = load_config(path)
            self.assertEqual(specs[0].name, "api")
            self.assertEqual(specs[0].cwd, root)

    def test_rejects_duplicate_names(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "x.json"
            path.write_text(json.dumps({"processes": [{"name": "x", "command": ["a"]}, {"name": "x", "command": ["b"]}]}), encoding="utf-8")
            with self.assertRaises(ConfigError): load_config(path)

    def test_rejects_shell_string(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "x.json"
            path.write_text(json.dumps({"processes": [{"name": "x", "command": "echo unsafe"}]}), encoding="utf-8")
            with self.assertRaises(ConfigError): load_config(path)


class LauncherTests(unittest.TestCase):
    def test_starts_and_waits_for_real_process(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = root / "x.json"
            cfg.write_text(json.dumps({"processes": [{"name": "worker", "command": [sys.executable, "-c", "print('ready')"]}]}), encoding="utf-8")
            launcher = Launcher(load_config(cfg), root / "logs")
            launcher.start()
            self.assertEqual(len(launcher.status()), 1)
            self.assertEqual(launcher.wait(), 0)
            launcher.stop()
            self.assertIn("ready", (root / "logs" / "worker.log").read_text(encoding="utf-8"))

    def test_stop_terminates_long_process(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = root / "x.json"
            cfg.write_text(json.dumps({"processes": [{"name": "worker", "command": [sys.executable, "-c", "import time; time.sleep(30)"]}]}), encoding="utf-8")
            launcher = Launcher(load_config(cfg), root / "logs")
            launcher.start(); time.sleep(.05); launcher.stop()
            self.assertEqual(launcher.running, [])


if __name__ == "__main__": unittest.main()
