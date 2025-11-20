from hackeros.cli import app

def test_version(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "hackeros" in result.stdout
