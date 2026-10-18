from pathlib import Path
import re
import sys


WORKFLOW_PATTERN = re.compile(
    r"workflow\s+([A-Za-z_]\w*)\s*\{(.*?)\}",
    re.DOTALL,
)

SAY_PATTERN = re.compile(
    r'say\s+"([^"]*)"'
)


def run_file(filename: str) -> None:
    source = Path(filename).read_text(encoding="utf-8")

    workflow = WORKFLOW_PATTERN.fullmatch(source.strip())

    if workflow is None:
        raise SyntaxError(
            "Expected: workflow Name { ... }"
        )

    name, body = workflow.groups()

    statements = []
    for line_number, line in enumerate(body.splitlines(), start=1):
        line = line.strip()

        if not line:
            continue

        match = SAY_PATTERN.fullmatch(line)
        if match is None:
            raise SyntaxError(
                f"Invalid statement on body line {line_number}: {line}"
            )

        statements.append(match.group(1))

    print(f"Running workflow: {name}")

    for message in statements:
        print(message)

    print("Workflow completed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python nyra.py <file.nyra>")
        raise SystemExit(2)

    try:
        run_file(sys.argv[1])
    except (SyntaxError, OSError) as error:
        print(f"Nyravelle error: {error}", file=sys.stderr)
        raise SystemExit(1)