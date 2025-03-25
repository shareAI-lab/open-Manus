from docker import DockerClient
from docker.errors import NotFound, DockerException

client = DockerClient()


async def create_container():
    try:

        container = client.containers.create(
            "box-2",
            detach=True,
            mem_limit="512m",
            network_mode="host",
        )

        container.start()

        _, output = container.exec_run(
            cmd=["mkdir", "-p", "/app"],
            user="root",
        )

        return container
    except DockerException as e:
        raise


async def execute_command(container_id: str, command: str):
    try:
        container = client.containers.get(container_id)
        exit_code, output = container.exec_run(
            cmd=["/bin/bash", "-c", command],
            workdir="/app",
            user="root",
            stream=False,
        )
        return output.decode("utf-8")
    except DockerException as e:
        raise


async def delete_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.stop()
        container.remove()
    except DockerException as e:
        raise
