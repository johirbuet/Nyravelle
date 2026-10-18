from nyra import run_file


def test_runs_a_simple_workflow(tmp_path, capsys):
    program = tmp_path / "hello.nyra"

    program.write_text(
        'workflow Hello {\n'
        '    say "Hello!"\n'
        '}\n',
        encoding="utf-8",
    )

    run_file(str(program))

    output = capsys.readouterr().out

    assert "Running workflow: Hello" in output
    assert "Hello!" in output
    assert "Workflow completed." in output


def test_rejects_invalid_statement(tmp_path):
    program = tmp_path / "invalid.nyra"

    program.write_text(
        "workflow Broken {\n"
        "    unknown_command\n"
        "}\n",
        encoding="utf-8",
    )

    import pytest

    with pytest.raises(SyntaxError):
        run_file(str(program))