from __future__ import annotations

import json
from importlib import resources
from typing import Any


def load_llm_judge_rubric() -> dict[str, Any]:
    rubric_path = resources.files("handovergap.data").joinpath("llm_judge_rubric.json")
    return json.loads(rubric_path.read_text())
