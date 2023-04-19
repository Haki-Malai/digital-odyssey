from click.testing import CliRunner

from app.cli import fake


def test_fake():
    """Test that fake data is generated.
    """
    runner = CliRunner()

    result = runner.invoke(fake)
    assert result.exit_code == 0
