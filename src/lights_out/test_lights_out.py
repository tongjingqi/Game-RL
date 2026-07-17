"""Regression tests for the Lights Out engineering pipeline."""

import hashlib
import importlib.util
import os
import random
import tempfile
import unittest

from PIL import Image

from lights_out import _layout, build_task2, generate_board, render_board


HERE = os.path.dirname(os.path.abspath(__file__))


def load_local_module(name, filename):
    path = os.path.join(HERE, filename)
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


class CoreRegressionTests(unittest.TestCase):
    def test_task2_b_returns_its_complete_option_set(self):
        grid, _ = generate_board(3, 2, random.Random(1))
        _, options, correct, _ = build_task2(grid, "B", random.Random(2))
        self.assertEqual(len(options), 8)
        self.assertEqual(len(options), len(set(options)))
        self.assertIn(correct, options)

    def test_all_board_sizes_render_within_the_image_budget(self):
        for size in (3, 4, 5):
            with self.subTest(size=size):
                width, height = _layout(size)[-2:]
                self.assertLessEqual(max(width, height), 640)
                grid, _ = generate_board(size, 1, random.Random(size))
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, "board.png")
                    render_board(grid, path)
                    with Image.open(path) as image:
                        self.assertEqual(image.format, "PNG")
                        self.assertEqual(image.mode, "RGB")
                        self.assertEqual(image.size, (width, height))


class DatasetPipelineTests(unittest.TestCase):
    def test_generated_dataset_passes_the_independent_verifier(self):
        generator = load_local_module("lights_out_main_test", "main.py")
        verifier = load_local_module("lights_out_verify_test", "verify.py")
        with tempfile.TemporaryDirectory() as output_dir:
            original_output = generator.OUTPUT_DIR
            original_dataset = verifier.DATASET_DIR
            original_data = verifier.DATA_PATH
            try:
                generator.OUTPUT_DIR = output_dir
                generator.main()
                verifier.DATASET_DIR = output_dir
                verifier.DATA_PATH = os.path.join(output_dir, "data.json")
                verifier.errors.clear()
                verifier.checks = 0
                result = verifier.main()
            finally:
                generator.OUTPUT_DIR = original_output
                verifier.DATASET_DIR = original_dataset
                verifier.DATA_PATH = original_data
            self.assertEqual(result, 0)

    def test_generator_is_deterministic_for_the_full_output_tree(self):
        generator = load_local_module("lights_out_main_determinism", "main.py")
        original_output = generator.OUTPUT_DIR
        try:
            with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
                generator.OUTPUT_DIR = first
                generator.main()
                generator.OUTPUT_DIR = second
                generator.main()
                self.assertEqual(tree_hash(first), tree_hash(second))
        finally:
            generator.OUTPUT_DIR = original_output


class DocumentationTests(unittest.TestCase):
    def test_readme_and_requirements_cover_the_supported_workflow(self):
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as handle:
            readme = handle.read()
        for heading in (
            "# Lights Out VQA Dataset Generator",
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
        with open(os.path.join(HERE, "requirements.txt"), encoding="utf-8") as handle:
            requirements = handle.read().splitlines()
        self.assertIn("Pillow==11.3.0", requirements)
        self.assertIn("numpy>=1.26", requirements)


if __name__ == "__main__":
    unittest.main()
