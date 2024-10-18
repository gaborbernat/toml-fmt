"""Main entry point for the formatter."""

from __future__ import annotations

from argparse import ArgumentParser, ArgumentTypeError
from typing import Sequence

from ._lib import Settings, format_toml
from .toml_fmt_common import FmtNamespace, TOMLFormatter, run


class PyProjectFmtNamespace(FmtNamespace):
    keep_full_version: bool
    max_supported_python: tuple[int, int]


class PyProjectFormatter(TOMLFormatter[PyProjectFmtNamespace]):
    def __init__(self) -> None:
        super().__init__(PyProjectFmtNamespace())

    @property
    def prog(self) -> str:
        return "pyproject-fmt"

    @property
    def filename(self) -> str:
        return "pyproject.toml"

    def add_format_flags(self, parser: ArgumentParser) -> None:
        msg = "keep full dependency versions - do not remove redundant .0 from versions"
        parser.add_argument("--keep-full-version", action="store_true", help=msg)

        def _version_argument(got: str) -> tuple[int, int]:
            parts = got.split(".")
            if len(parts) != 2:  # noqa: PLR2004
                err = f"invalid version: {got}, must be e.g. 3.13"
                raise ArgumentTypeError(err)
            try:
                return int(parts[0]), int(parts[1])
            except ValueError as exc:
                err = f"invalid version: {got} due {exc!r}, must be e.g. 3.13"
                raise ArgumentTypeError(err) from exc

        parser.add_argument(
            "--max-supported-python",
            metavar="minor.major",
            type=_version_argument,
            default=(3, 13),
            help="latest Python version the project supports (e.g. 3.13)",
        )

    @property
    def override_cli_from_section(self) -> tuple[str, ...]:
        return "tool", "pyproject-fmt"

    def format(self, content: str, opt: PyProjectFmtNamespace) -> str:
        settings = Settings(
            column_width=opt.column_width,
            indent=opt.indent,
            keep_full_version=opt.keep_full_version,
            max_supported_python=opt.max_supported_python,
            min_supported_python=(3, 9),  # default for when the user did not specify via requires-python
        )
        return format_toml(content, settings)


def runner(args: Sequence[str] | None = None) -> int:
    return run(PyProjectFormatter(), args)


if __name__ == "__main__":
    raise SystemExit(runner())
