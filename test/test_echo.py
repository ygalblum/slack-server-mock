from pathlib import Path
import time
import subprocess

import pytest
import requests
from slackbot import EchoSlackBot


# Fixture to manage Podman container lifecycle
@pytest.fixture(scope="module")
def podman_container():
    container_name = "slack_server_mock"
    image = "slack_server_mock:latest"
    ports = [3001, 8080, 8888]
    project_root_path = Path(__file__).parents[1]
    volumes = [f"{project_root_path}/settings.yaml:/app/settings.yaml:z"]

    podman_run_command = ["podman", "run", "--name", container_name, "-d", "--rm"]
    for port in ports:
        podman_run_command.extend(["--publish", f"{port}:{port}"])
    for volume in volumes:
        podman_run_command.extend(["--volume", volume])
    podman_run_command.append(image)
    # Start the container
    print("Starting Podman container...")
    subprocess.run(podman_run_command, check=True)

    # Wait a bit for the container to be fully up and running
    time.sleep(5)

    # Provide the container name to the test
    yield container_name

    # Stop and remove the container after tests
    print("Stopping Podman container...")
    subprocess.run(["podman", "kill", container_name], check=True)


@pytest.fixture
def bot():
    bot = EchoSlackBot()
    bot.run()
    while not bot.is_connected():
        time.sleep(1)
    yield bot
    bot.stop()


def test_echo(bot, podman_container):
    msg = "foo"
    res = requests.post(url="http://localhost:8080/message", json={"message": msg})
    assert res.json().get('answer') == msg
