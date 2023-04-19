import click
from click.testing import CliRunner

from app.cli import fake, test


def test_fake():
    """Test that fake data is generated.
    """
    runner = CliRunner()
    result = runner.invoke(fake)
    assert result.exit_code == 0


def test_test():
    """Test that tests are able to run.
    """
    runner = CliRunner()
    result = runner.invoke(test, ['-c', '-d', 'tests'])
    assert result.exit_code == 0
