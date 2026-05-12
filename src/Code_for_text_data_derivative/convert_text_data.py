"""Unified converter from multimodal game QA data to text-only QA data."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from game_text_adapters import ADAPTERS, get_adapter


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write("\n")


def resolve_state_path(data_path: Path, state_path: str) -> Path:
    raw = Path(state_path)
    candidates = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend(
            [
                data_path.parent / raw,
                Path.cwd() / raw,
                data_path.parent / "states" / raw.name,
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"State file not found for {state_path!r}; tried: {candidates}")


def infer_game_from_path(data_path: Path) -> str | None:
    parts = list(data_path.resolve().parts)
    if "src" not in parts:
        return None
    src_index = parts.index("src")
    if src_index + 1 >= len(parts):
        return None
    game = parts[src_index + 1]
    return game if game in ADAPTERS else None


def make_text_question(state_text: str, original_question: str) -> str:
    return (
        "Instead of an image, use the following text representation of the visible game state.\n\n"
        f"{state_text.strip()}\n\n"
        "QUESTION:\n"
        f"{original_question.strip()}"
    )


def convert_dataset(
    game: str,
    data_path: Path,
    output_path: Path,
    *,
    keep_image: bool = False,
    keep_state: bool = False,
) -> list[dict[str, Any]]:
    adapter = get_adapter(game)
    data = read_json(data_path)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list in {data_path}, got {type(data).__name__}")

    converted = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Entry {index} is not a JSON object")
        if "state" not in item:
            raise KeyError(f"Entry {item.get('data_id', index)} has no state field")
        state_path = resolve_state_path(data_path, item["state"])
        state_data = read_json(state_path)
        if not isinstance(state_data, dict):
            raise ValueError(f"State file {state_path} must contain a JSON object")

        state_text = adapter(state_data, item)
        new_item = deepcopy(item)
        new_item["question"] = make_text_question(state_text, item.get("question", ""))
        if not keep_image:
            new_item.pop("image", None)
        if not keep_state:
            new_item.pop("state", None)
        converted.append(new_item)

    write_json(output_path, converted)
    return converted


def run_cli(default_game: str | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", default=default_game, help="Game adapter name. If omitted, infer from a src/<game>/... path when possible.")
    parser.add_argument("--data", default="data.json", help="Input data.json path.")
    parser.add_argument("--output", default="data_text.json", help="Output text-only JSON path.")
    parser.add_argument("--keep-image", action="store_true", help="Keep the original image field.")
    parser.add_argument("--keep-state", action="store_true", help="Keep the original state field.")
    parser.add_argument("--list-games", action="store_true", help="List registered game adapters and exit.")
    args = parser.parse_args()

    if args.list_games:
        for game in sorted(ADAPTERS):
            print(game)
        return

    data_path = Path(args.data).resolve()
    output_path = Path(args.output).resolve()
    game = args.game or infer_game_from_path(data_path)
    if not game:
        raise SystemExit("Could not infer game. Pass --game explicitly.")

    converted = convert_dataset(
        game,
        data_path,
        output_path,
        keep_image=args.keep_image,
        keep_state=args.keep_state,
    )
    print(f"Converted {len(converted)} entries for {game}: {output_path}")


if __name__ == "__main__":
    run_cli()
