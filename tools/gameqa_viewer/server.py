"""Local GameQA example-data viewer.

Run from the repository root:
    python tools/gameqa_viewer/server.py
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import posixpath
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pretty_game_name(game_id: str) -> str:
    special = {
        "3DReconstruction": "3D Reconstruction",
        "PyramidChess": "Pyramid Chess",
        "star-battle": "Star Battle",
        "ultra_tictactoe": "Ultra TicTacToe",
        "tictactoe": "TicTacToe",
        "2d_turing_machine": "2D Turing Machine",
        "3d_maze": "3D Maze",
    }
    if game_id in special:
        return special[game_id]
    return game_id.replace("_", " ").replace("-", " ").title()


def compact_text(value, limit: int = 160) -> str:
    if value is None:
        return ""
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def normalize_options(sample: dict):
    if "options" in sample:
        return sample.get("options")
    return sample.get("Options")


def normalize_answer(sample: dict):
    return sample.get("answer", sample.get("Answer"))


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class GameRegistry:
    def __init__(self, root: Path):
        self.root = root
        self.games = {}
        self.scan()

    def scan(self):
        games = {}
        for data_path in sorted((self.root / "src").glob("*/*dataset_example/data.json")):
            game_dir = data_path.parents[1]
            game_id = game_dir.name
            dataset_dir = data_path.parent
            try:
                samples = load_json(data_path)
            except Exception as exc:
                samples = []
                load_error = str(exc)
            else:
                load_error = None
            if not isinstance(samples, list):
                load_error = f"Expected a list in {data_path.name}, got {type(samples).__name__}"
                samples = []

            keys = sorted({key for row in samples if isinstance(row, dict) for key in row})
            image_missing, state_missing = self._count_missing_refs(dataset_dir, samples)
            games[game_id] = {
                "id": game_id,
                "name": pretty_game_name(game_id),
                "game_dir": game_dir,
                "dataset_dir": dataset_dir,
                "data_path": data_path,
                "samples": samples,
                "load_error": load_error,
                "keys": keys,
                "image_missing": image_missing,
                "state_missing": state_missing,
            }
        self.games = games

    def list_games(self):
        payload = []
        for game in sorted(self.games.values(), key=lambda item: item["name"].lower()):
            samples = [row for row in game["samples"] if isinstance(row, dict)]
            payload.append(
                {
                    "id": game["id"],
                    "name": game["name"],
                    "dataset": game["dataset_dir"].name,
                    "data_path": str(game["data_path"].relative_to(self.root)),
                    "count": len(samples),
                    "keys": game["keys"],
                    "qa_types": sorted({str(row.get("qa_type")) for row in samples if row.get("qa_type") is not None}),
                    "qa_levels": sorted({str(row.get("qa_level")) for row in samples if row.get("qa_level") is not None}),
                    "plot_levels": sorted({str(row.get("plot_level")) for row in samples if row.get("plot_level") is not None}),
                    "image_missing": game["image_missing"],
                    "state_missing": game["state_missing"],
                    "load_error": game["load_error"],
                }
            )
        return payload

    def list_samples(self, game_id: str):
        game = self._require_game(game_id)
        return [self._sample_summary(game, sample, index) for index, sample in enumerate(game["samples"]) if isinstance(sample, dict)]

    def sample_detail(self, game_id: str, index: int):
        game = self._require_game(game_id)
        if index < 0 or index >= len(game["samples"]):
            raise KeyError(f"Sample index {index} is out of range")
        sample = game["samples"][index]
        if not isinstance(sample, dict):
            raise KeyError(f"Sample index {index} is not an object")

        state_content = None
        state_error = None
        state_ref = sample.get("state")
        if isinstance(state_ref, str) and state_ref:
            state_path = self.resolve_data_path(game_id, state_ref)
            if state_path.exists():
                try:
                    state_content = load_json(state_path)
                except Exception as exc:
                    state_error = str(exc)
            else:
                state_error = f"Missing state file: {state_ref}"

        detail = self._sample_summary(game, sample, index)
        detail.update(
            {
                "question": sample.get("question", sample.get("Question")),
                "answer": normalize_answer(sample),
                "analysis": sample.get("analysis"),
                "options": normalize_options(sample),
                "state_content": state_content,
                "state_error": state_error,
                "raw": sample,
            }
        )
        return detail

    def resolve_data_path(self, game_id: str, rel_path: str):
        game = self._require_game(game_id)
        clean = rel_path.replace("\\", "/").lstrip("/")
        candidate = (game["dataset_dir"] / clean).resolve()
        dataset_root = game["dataset_dir"].resolve()
        if candidate != dataset_root and dataset_root not in candidate.parents:
            raise PermissionError("Path is outside the dataset directory")
        return candidate

    def _sample_summary(self, game: dict, sample: dict, index: int):
        image = sample.get("image")
        state = sample.get("state")
        options = normalize_options(sample)
        answer = normalize_answer(sample)
        question = sample.get("question", sample.get("Question"))
        return {
            "index": index,
            "data_id": sample.get("data_id"),
            "question_id": sample.get("question_id"),
            "question_description": sample.get("question_description"),
            "qa_type": sample.get("qa_type"),
            "qa_level": sample.get("qa_level"),
            "plot_level": sample.get("plot_level"),
            "answer": answer,
            "answer_preview": compact_text(answer, 80),
            "question_preview": compact_text(question),
            "image": image,
            "state": state,
            "image_url": self._data_url(game["id"], image) if isinstance(image, str) else None,
            "state_url": self._data_url(game["id"], state) if isinstance(state, str) else None,
            "has_options": isinstance(options, list) and len(options) > 0,
        }

    def _data_url(self, game_id: str, rel_path: str):
        return "/data/" + game_id + "/" + "/".join(part for part in rel_path.replace("\\", "/").split("/") if part)

    def _count_missing_refs(self, dataset_dir: Path, samples: list):
        image_missing = 0
        state_missing = 0
        for sample in samples:
            if not isinstance(sample, dict):
                continue
            for image in as_list(sample.get("image")):
                if isinstance(image, str) and image and not (dataset_dir / image).exists():
                    image_missing += 1
            for state in as_list(sample.get("state")):
                if isinstance(state, str) and state and not (dataset_dir / state).exists():
                    state_missing += 1
        return image_missing, state_missing

    def _require_game(self, game_id: str):
        if game_id not in self.games:
            raise KeyError(f"Unknown game: {game_id}")
        return self.games[game_id]


class GameQAHandler(BaseHTTPRequestHandler):
    registry: GameRegistry = None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        try:
            if path == "/":
                self._send_static(STATIC_DIR / "index.html")
            elif path.startswith("/static/"):
                self._send_static(STATIC_DIR / path.removeprefix("/static/"))
            elif path == "/api/games":
                self._send_json({"games": self.registry.list_games()})
            elif path.startswith("/api/games/"):
                self._handle_game_api(path)
            elif path.startswith("/data/"):
                self._handle_data_file(path)
            else:
                self._send_error(HTTPStatus.NOT_FOUND, "Not found")
        except PermissionError as exc:
            self._send_error(HTTPStatus.FORBIDDEN, str(exc))
        except KeyError as exc:
            self._send_error(HTTPStatus.NOT_FOUND, str(exc).strip("'"))
        except Exception as exc:
            self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _handle_game_api(self, path: str):
        parts = [part for part in path.split("/") if part]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "games" and parts[3] == "samples":
            self._send_json({"samples": self.registry.list_samples(parts[2])})
            return
        if len(parts) == 5 and parts[0] == "api" and parts[1] == "games" and parts[3] == "samples":
            self._send_json({"sample": self.registry.sample_detail(parts[2], int(parts[4]))})
            return
        self._send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")

    def _handle_data_file(self, path: str):
        parts = [part for part in path.split("/") if part]
        if len(parts) < 3:
            self._send_error(HTTPStatus.NOT_FOUND, "Missing data path")
            return
        game_id = parts[1]
        rel_path = posixpath.join(*parts[2:])
        data_path = self.registry.resolve_data_path(game_id, rel_path)
        self._send_static(data_path)

    def _send_static(self, path: Path):
        if not path.exists() or not path.is_file():
            self._send_error(HTTPStatus.NOT_FOUND, f"Missing file: {path.name}")
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_error(self, status, message):
        self._send_json({"error": message}, status)


def parse_args():
    parser = argparse.ArgumentParser(description="Serve a local GameQA example-data viewer.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind. Defaults to 8765.")
    return parser.parse_args()


def main():
    args = parse_args()
    registry = GameRegistry(ROOT_DIR)
    GameQAHandler.registry = registry
    server = ThreadingHTTPServer((args.host, args.port), GameQAHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"GameQA viewer serving {len(registry.games)} games at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping GameQA viewer")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
