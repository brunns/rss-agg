import os

import scripttest
from brunns.matchers.rss import is_rss_feed
from hamcrest import assert_that, contains_string, has_length


def test_cli_output():
    # Given
    env = scripttest.TestFileEnvironment()

    # When
    result = env.run("uv", "run", "cli", cwd=os.getcwd())

    # Then
    assert not result.returncode
    assert not result.stderr
    assert_that(result.stdout, is_rss_feed().with_entries(has_length(50)))


def test_cli_max_items():
    # Given
    env = scripttest.TestFileEnvironment()

    # When
    result = env.run("uv", "run", "cli", "-m10", cwd=os.getcwd())

    # Then
    assert not result.returncode
    assert not result.stderr
    assert_that(result.stdout, is_rss_feed().with_entries(has_length(10)))


def test_cli_help():
    # Given
    env = scripttest.TestFileEnvironment()

    # When
    result = env.run("uv", "run", "cli", "-h", cwd=os.getcwd())

    # Then
    assert not result.returncode
    assert not result.stderr
    assert_that(result.stdout, contains_string("Display status of GitHub Actions."))
