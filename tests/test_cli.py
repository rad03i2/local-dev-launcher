import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from local_dev_launcher.cli import main

class CliTests(unittest.TestCase):
    def test_check(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.json"
            p.write_text(json.dumps({"processes": [{"name": "x", "command": ["does-not-run-during-check"]}]}), encoding="utf-8")
            self.assertEqual(main(["check", str(p)]), 0)

    def test_bad_config_exit_code(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.json"; p.write_text("{}", encoding="utf-8")
            self.assertEqual(main(["check", str(p)]), 2)

if __name__ == "__main__": unittest.main()
