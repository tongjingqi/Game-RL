"""Batch-convert every registered game dataset example to text-only QA data."""

from __future__ import annotations

import argparse
from pathlib import Path

from convert_text_data import convert_dataset
from game_text_adapters import ADAPTERS


def find_dataset(root: Path, game: str) -> Path | None:
    game_dir = root / "src" / game
    if not game_dir.exists():
        return None
    candidates = sorted(game_dir.glob("*dataset_example/data.json"))
    if candidates:
        return candidates[0]
    candidates = sorted(game_dir.glob("**/data.json"))
    return candidates[0] if candidates else None


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--dry-run", action="store_true", help="Only print planned conversions.")
    parser.add_argument("--keep-image", action="store_true", help="Keep image fields in outputs.")
    parser.add_argument("--keep-state", action="store_true", help="Keep state fields in outputs.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    games = sorted(
        game_dir.name
        for game_dir in (root / "src").iterdir()
        if game_dir.is_dir()
        and game_dir.name != "Code_for_text_data_derivative"
        and game_dir.name in ADAPTERS
    )
    for game in games:
        data_path = find_dataset(root, game)
        if not data_path:
            print(f"Skip {game}: no data.json found")
            continue
        output_path = data_path.parent / "data_text.json"
        if args.dry_run:
            print(f"Would convert {game}: {data_path} -> {output_path}")
            continue
        converted = convert_dataset(
            game,
            data_path,
            output_path,
            keep_image=args.keep_image,
            keep_state=args.keep_state,
        )
        print(f"Converted {game}: {len(converted)} entries -> {output_path}")


if __name__ == "__main__":
    run()
