"""Focused regression tests for the Tower of Hanoi renderer."""

import os
import hashlib
import importlib.util
import json
import tempfile
import unittest

from PIL import Image

from tower_of_hanoi import render_board


HERE = os.path.dirname(os.path.abspath(__file__))
EXPECTED_FIELDS = [
    "data_id",
    "image",
    "state",
    "plot_level",
    "qa_level",
    "qa_type",
    "question_id",
    "question_description",
    "question",
    "answer",
    "analysis",
    "options",
]


def load_local_module(name, filename):
    path = os.path.join(HERE, filename)
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_hash(root):
    digest = hashlib.sha256()
    for current, dirs, files in os.walk(root):
        dirs.sort()
        for filename in sorted(files):
            path = os.path.join(current, filename)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            digest.update(rel.encode("utf-8"))
            with open(path, "rb") as handle:
                digest.update(handle.read())
    return digest.hexdigest()


class RenderBoardTests(unittest.TestCase):
    def test_render_board_writes_expected_png(self):
        state = {
            "num_disks": 5,
            "pegs": {"A": [5, 3, 1], "B": [4, 2], "C": []},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "board.png")
            render_board(state, path)

            with Image.open(path) as image:
                self.assertEqual(image.format, "PNG")
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(image.size, (600, 580))


class DatasetPipelineTests(unittest.TestCase):
    def test_generator_output_passes_independent_verifier(self):
        generator = load_local_module("tower_of_hanoi_main", "main.py")
        verifier = load_local_module("tower_of_hanoi_verify", "verify.py")
        self.assertIsNotNone(generator, "main.py is required")
        self.assertIsNotNone(verifier, "verify.py is required")

        with tempfile.TemporaryDirectory() as output_dir:
            generator.main(output_dir)
            with open(os.path.join(output_dir, "data.json"), encoding="utf-8") as handle:
                data = json.load(handle)

            self.assertEqual(len(data), 60)
            self.assertEqual(
                [len({e["image"] for e in data if e["plot_level"] == level})
                 for level in ("Easy", "Medium", "Hard")],
                [5, 5, 5],
            )
            self.assertTrue(all(list(entry) == EXPECTED_FIELDS for entry in data))
            self.assertTrue(all(entry["options"][entry["answer"] - 1] in entry["analysis"]
                                for entry in data))

            failures, counts = verifier.check_dataset(output_dir)
            self.assertEqual(failures, [])
            self.assertEqual(counts, {1: 15, 2: 15, 3: 15, 4: 15})

    def test_generator_is_deterministic_for_the_full_output_tree(self):
        generator = load_local_module("tower_of_hanoi_main_determinism", "main.py")
        self.assertIsNotNone(generator, "main.py is required")

        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            generator.main(first)
            generator.main(second)
            self.assertEqual(tree_hash(first), tree_hash(second))


class DocumentationTests(unittest.TestCase):
    def test_readme_and_requirements_cover_the_supported_workflow(self):
        readme_path = os.path.join(HERE, "README.md")
        requirements_path = os.path.join(HERE, "requirements.txt")
        self.assertTrue(os.path.isfile(readme_path), "README.md is required")
        self.assertTrue(os.path.isfile(requirements_path), "requirements.txt is required")

        with open(readme_path, encoding="utf-8") as handle:
            readme = handle.read()
        for heading in (
            "# Tower of Hanoi VQA Dataset Generator",
            "## Features",
            "## Game Rules",
            "## Project Structure",
            "## Supported Question Types",
            "## Usage",
            "## License",
        ):
            self.assertIn(heading, readme)
        self.assertIn("python main.py", readme)
        self.assertIn("python verify.py", readme)

        with open(requirements_path, encoding="utf-8") as handle:
            self.assertEqual(handle.read().strip(), "Pillow==11.3.0")


if __name__ == "__main__":
    unittest.main()
