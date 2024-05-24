#!/usr/bin/env python
"""Update usage string in README from actual usage string."""

from pathlib import Path
from subprocess import run


def main() -> None:  # noqa: D103
    encoding = "UTF-8"
    readme = Path(__file__).parent.parent / "README.rst"
    usage_string_lines = [
        f"    {line.rstrip()}".rstrip()
        for line in run(
            ["cpac", "--help", "|", "sed", "'s/^/    /'"],
            capture_output=True,
            check=False,
        )
        .stdout.decode()
        .split("\n")
    ]
    lines = []
    with readme.open("r", encoding=encoding) as _readme:
        usage_lines = False
        for line in _readme.readlines():
            if line.lstrip().startswith(".. END USAGE"):
                usage_lines = False
            if not usage_lines:
                lines.append(f"{line.rstrip()}")
            if line.lstrip().startswith(".. BEGIN USAGE"):
                usage_lines = True
                lines += [
                    ".. code-block:: shell",
                    "",
                    "    cpac --help",
                    *usage_string_lines,
                ]
    with readme.open("w", encoding=encoding) as _readme:
        _readme.write("\n".join([*lines, ""]))


main.__doc__ == __doc__
if __name__ == "__main__":
    main()
