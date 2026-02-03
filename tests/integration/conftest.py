import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import pytest
from httpx import RequestError
from mbtest.server import MountebankServer
from yarl import URL

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def mountebank_instance(docker_ip, docker_services) -> URL:
    port = docker_services.port_for("mountebank", 2525)
    url = URL(f"http://{docker_ip}:{port}")
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_responsive(url))
    return url


@pytest.fixture(scope="session")
def mock_server(mountebank_instance: URL) -> MountebankServer:
    return MountebankServer(host=mountebank_instance.host, port=mountebank_instance.port)


def is_responsive(url: URL) -> bool:
    try:
        response = httpx.get(str(url))
        response.raise_for_status()
    except RequestError:
        return False
    else:
        return True


@pytest.fixture
def sausages_feeds_file() -> Generator[Path]:
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        tf.write("sausages")
        feeds_file = Path(tf.name)

    try:
        yield feeds_file
    finally:
        if feeds_file.exists():
            feeds_file.unlink()
