import re
import sys
from pathlib import Path

WORKFLOW_PATTERN = re.compile(
    r"workflow\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{"
)

INPUT_PATTERN = re.compile(
    r"input\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"\s*:\s*(string|number|boolean)"
)

SAY_PATTERN = re.compile(
    r'say\s+"((?:[^"\\]|\\.)*)"\s*'
)

def validate_source(source):
    """
    Validate the small subset of Nyravelle supported today.
    Supported:
      - One workflow declaration
      - Input declarations with basic types
      - Simple say statements
    This is a bootstrap validator, not a full parser.
    """
    errors = []
    inputs = []
    messages = []
    lines = source.splitlines()
    # Ignore blank lines when checking the outer structure.
    nonempty = [
        (number, line.strip())
        for number, line in enumerate(lines, start=1)
        if line.strip()
    ]
    if not nonempty:
        return {
            "workflow": None,
            "inputs": [],
            "messages": [],
            "errors": ["The source file is empty."],
        }
    first_line_number, first_line = nonempty[0]
    last_line_number, last_line = nonempty[-1]
    match = WORKFLOW_PATTERN.fullmatch(first_line)
    if not match:
        errors.append(
            f"Line {first_line_number}: "
            "expected 'workflow Name {' at the beginning."
        )
        workflow_name = None
    else:
        workflow_name = match.group(1)
    if last_line != "}":
        errors.append(
            f"Line {last_line_number}: "
            "expected '}' to close the workflow."
        )
    if workflow_name is not None and match:
        # Check for an extra closing brace before the final line.
        for number, line in nonempty[1:-1]:
            if line == "}":
                errors.append(
                    f"Line {number}: unexpected closing brace."
                )
    declared_inputs = set()
    # The first and last nonempty lines delimit the workflow.
    # Nested blocks and multiline statements are not supported.
    for number, original_line in enumerate(lines, start=1):
        line = original_line.strip()
        if not line:
            continue
        if number == first_line_number or number == last_line_number:
            continue
        input_match = INPUT_PATTERN.fullmatch(line)
        if input_match:
            name, type_name = input_match.groups()
            if name in declared_inputs:
                errors.append(
                    f"Line {number}: duplicate input '{name}'."
                )
            else:
                declared_inputs.add(name)
                inputs.append({
                    "name": name,
                    "type": type_name,
                })
            continue
        say_match = SAY_PATTERN.fullmatch(line)
        if say_match:
            messages.append(say_match.group(1))
            continue
        errors.append(
            f"Line {number}: unsupported statement: {line}"
        )
    return {
        "workflow": workflow_name,
        "inputs": inputs,
        "messages": messages,
        "errors": errors,
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python nyra.py <file.nyra>")
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Error: file not found: {path}")
        return 2
    source = path.read_text(encoding="utf-8")
    result = validate_source(source)
    if result["errors"]:
        print("Validation failed:")
        for error in result["errors"]:
            print(f"  - {error}")
        return 1
    print(f"Workflow: {result['workflow']}")
    print("Validation successful.")
    for item in result["inputs"]:
        print(f"Input: {item['name']} ({item['type']})")
    for message in result["messages"]:
        print(f"Message: {message}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())