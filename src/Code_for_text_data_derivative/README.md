# Text QA Conversion

This directory provides a unified conversion path from multimodal game QA data
to text-only QA data.

## Convert One Dataset

Run from a dataset example directory:

```bash
python ../../Code_for_text_data_derivative/convert_text_data.py --game sokoban
```

Or pass paths explicitly from the repository root:

```bash
python src/Code_for_text_data_derivative/convert_text_data.py \
  --game sokoban \
  --data src/sokoban/sokoban_dataset_example/data.json \
  --output src/sokoban/sokoban_dataset_example/data_text.json
```

The default output removes `image` and `state` fields and prepends a text
description of the visible game state to each question.

## Convert All Dataset Examples

```bash
python src/Code_for_text_data_derivative/convert_all_text_data.py
```

Preview planned conversions without writing files:

```bash
python src/Code_for_text_data_derivative/convert_all_text_data.py --dry-run
```

## Adapter Design

The shared runner handles JSON IO, state-path resolution, UTF-8 encoding,
question rewriting, and output writing. Game-specific logic lives in
`game_text_adapters.py`.

Adapters should describe only information that is visible in the rendered game
state or necessary rules already present in the prompt. They must avoid exposing
solution-only fields such as hidden best moves, completed boards, or answer
paths.
