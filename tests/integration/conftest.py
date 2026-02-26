import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx
import pytest
from httpx import RequestError
from mbtest.server import MountebankServer
from yarl import URL

if TYPE_CHECKING:
    from collections.abc import Generator

    from pytest_docker import Services

GARAGE_ADMIN_TOKEN = "test-admin-token"
GARAGE_REGION = "garage"
GARAGE_BUCKET = "test-feeds"
GARAGE_KEY_NAME = "test-key"


@pytest.fixture(scope="session")
def mountebank_instance(docker_ip: str, docker_services: Services) -> URL:
    port = docker_services.port_for("mountebank", 2525)
    url = URL(f"http://{docker_ip}:{port}")
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_responsive(url))
    return url


@pytest.fixture(scope="session")
def mock_server(mountebank_instance: URL) -> MountebankServer:
    return MountebankServer(host=mountebank_instance.host, port=mountebank_instance.port)


@pytest.fixture(scope="session")
def garage_instance(docker_ip, docker_services: Services) -> URL:
    admin_port = docker_services.port_for("garage", 3903)
    admin_url = URL(f"http://{docker_ip}:{admin_port}")
    check_url = admin_url / "v2" / "GetClusterStatus"
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_garage_responsive(check_url))
    return admin_url


@pytest.fixture(scope="session")
def s3_config(garage_instance: URL, docker_ip: str, docker_services: Services) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}"}

    with httpx.Client() as client:
        status_response = client.get(str(garage_instance / "v2" / "GetClusterStatus"), headers=headers)
        status_response.raise_for_status()
        node_id = status_response.json()["nodes"][0]["id"]

        client.post(
            str(garage_instance / "v2" / "UpdateClusterLayout"),
            headers=headers,
            json={"roles": [{"id": node_id, "zone": "dc1", "capacity": 1_000_000_000, "tags": []}]},
        ).raise_for_status()

        client.post(
            str(garage_instance / "v2" / "ApplyClusterLayout"),
            headers=headers,
            json={"version": 1},
        ).raise_for_status()

        bucket_response = client.post(
            str(garage_instance / "v2" / "CreateBucket"),
            headers=headers,
            json={"globalAlias": GARAGE_BUCKET},
        )
        bucket_response.raise_for_status()
        bucket_id = bucket_response.json()["id"]

        key_response = client.post(
            str(garage_instance / "v2" / "CreateKey"),
            headers=headers,
            json={"name": GARAGE_KEY_NAME},
        )
        key_response.raise_for_status()
        access_key_id = key_response.json()["accessKeyId"]
        secret_access_key = key_response.json()["secretAccessKey"]

        client.post(
            str(garage_instance / "v2" / "AllowBucketKey"),
            headers=headers,
            json={
                "bucketId": bucket_id,
                "accessKeyId": access_key_id,
                "permissions": {"read": True, "write": True, "owner": False},
            },
        ).raise_for_status()

    s3_port = docker_services.port_for("garage", 3900)
    return {
        "aws_default_region": GARAGE_REGION,
        "aws_access_key_id": access_key_id,
        "aws_secret_access_key": secret_access_key,
        "s3_endpoint": URL(f"http://{docker_ip}:{s3_port}"),
        "feeds_bucket_name": GARAGE_BUCKET,
    }


def is_responsive(url: URL) -> bool:
    try:
        response = httpx.get(str(url))
        response.raise_for_status()
    except RequestError:
        return False
    else:
        return True


def is_garage_responsive(url: URL) -> bool:
    try:
        response = httpx.get(str(url), headers={"Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}"})
        response.raise_for_status()
    except httpx.RequestError, httpx.HTTPStatusError:
        return False
    else:
        return True


@pytest.fixture(scope="session")
def sausages_feeds_file() -> Generator[Path]:
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        tf.write("sausages")
        feeds_file = Path(tf.name)

    try:
        yield feeds_file
    finally:
        if feeds_file.exists():
            feeds_file.unlink()
