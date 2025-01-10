#!/usr/bin/env python3
"""Store optional dependencies for dynamic metadata access."""

from itertools import chain
from pathlib import Path
from pickle import dump, load
import tomllib
from typing import cast

from packaging.requirements import Requirement

PICKLE_PATH = Path(__file__).parents[1] / "optional_dependencies.pkl"


def store_optional_dependencies(output_path: str) -> None:
    """Store optional dependencies."""
    # Extract optional dependencies
    with open("pyproject.toml", "rb") as f:
        toml_data = tomllib.load(f)
    optional_deps: dict[str, Requirement] = {}
    reqs = [
        Requirement(req)
        for req in chain.from_iterable(
            toml_data.get("project", {}).get("optional-dependencies", {}).values()
        )
    ]
    for req in reqs:
        if req.name in optional_deps:
            optional_deps[req.name].specifier &= req.specifier
        else:
            optional_deps[req.name] = req

    with open(output_path, "rb") as f:
        existing_optional_deps = cast(dict[str, Requirement], load(f))
    if not optional_deps == existing_optional_deps:
        with open(output_path, "wb") as f:
            dump(optional_deps, f)


if __name__ == "__main__":
    store_optional_dependencies(str(PICKLE_PATH))
