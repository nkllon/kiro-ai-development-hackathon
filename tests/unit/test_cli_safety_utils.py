"""Unit tests for the extracted CLI safety utilities."""

from cli_safety import EmergencyCLIFix, SafeShellWrapper, safe_run


def test_emergency_cli_fix_rejects_unbalanced_quotes() -> None:
    cli_fix = EmergencyCLIFix()
    ok, reason = cli_fix.validate_command('echo "unterminated')
    assert not ok
    assert "UNBALANCED" in reason or "DANGEROUS" in reason


def test_safe_shell_wrapper_rejects_invalid_command() -> None:
    wrapper = SafeShellWrapper()
    ok, stdout, stderr = wrapper.safe_execute('echo "unterminated')
    assert not ok
    assert "COMMAND REJECTED" in stdout
    assert stderr == ""


def test_safe_run_success(tmp_path) -> None:
    script = tmp_path / "hello.sh"
    script.write_text("echo hello")
    ok, stdout, stderr = safe_run(f"bash {script}")
    assert ok
    assert stdout.strip() == "hello"
    assert stderr == ""

