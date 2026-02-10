import os

import scripttest
from brunns.matchers.rss import is_rss_feed
from brunns.matchers.scripttest import is_proc_result
from hamcrest import assert_that, contains_string, has_length
from mbtest.imposters import Imposter, Predicate, Response, Stub


def test_cli_output(mock_server, large_rss_string, sausages_feeds_file):
    # Given
    env = scripttest.TestFileEnvironment()
    imposter = Imposter(Stub(Predicate(path="/sausages/rss"), Response(body=large_rss_string)), port=4545)

    with mock_server(imposter):
        # When
        result = env.run(
            "uv", "run", "cli", "--feeds-file", sausages_feeds_file, "--base-url", imposter.url, cwd=os.getcwd()
        )

    # Then
    assert_that(
        result,
        is_proc_result().with_returncode(0).with_stderr("").with_stdout(is_rss_feed().with_entries(has_length(50))),
    )


def test_cli_max_items(mock_server, large_rss_string, sausages_feeds_file):
    # Given
    env = scripttest.TestFileEnvironment()
    imposter = Imposter(Stub(Predicate(path="/sausages/rss"), Response(body=large_rss_string)), port=4545)

    # When
    with mock_server(imposter):
        result = env.run(
            "uv", "run", "cli", "--feeds-file", sausages_feeds_file, "--base-url", imposter.url, "-m10", cwd=os.getcwd()
        )

    # Then
    assert_that(
        result,
        is_proc_result().with_returncode(0).with_stderr("").with_stdout(is_rss_feed().with_entries(has_length(10))),
    )


def test_cli_help():
    # Given
    env = scripttest.TestFileEnvironment()

    # When
    result = env.run("uv", "run", "cli", "-h", cwd=os.getcwd())

    # Then
    assert_that(
        result,
        is_proc_result()
        .with_returncode(0)
        .with_stderr("")
        .with_stdout(contains_string("Aggregate, de-duplicate and republish RSS feeds.")),
    )
