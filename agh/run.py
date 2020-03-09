# -*- utf-8 -*-
import docker

class DockerContainer:

    docker_client = docker.from_env()
    containers = dict()

    def __init__(self, container_info):
        self.id = container_info.id
        self.name = container_info.name
        self.image = container_info.image
        self.status = container_info.status
        self._container = container_info
    
    def logs(self, tail = 100):
        logs = self._container.logs()
        print (logs)
        return logs

    def exec(self, command):
        if not command: raise Exception("command is necessary")
        code, logs = self._container.exec_run(command)
        print (code, logs)
        return logs

    def to_json(self):
        return dict(
            id=self.id,
            name= self.name,
            image=str(self.image),
            status=self.status
        )

    @staticmethod
    def load_containers(refresh = False):
        items = list()
        if refresh:
            DockerContainer.containers = dict()
        for container in DockerContainer.docker_client.containers.list():
            container = DockerContainer(container)
            DockerContainer.containers[container.id] = container
            items.append(container)
        return items

    @staticmethod
    def refresh_containers():
        return DockerContainer.load_containers(True)


# ============ REST Server Part ============

import json
from aiohttp import web

async def list_latest(request):
    result = list()
    for container in DockerContainer.refresh_containers():
        result.append(container.to_json())
    return web.Response(text=json.dumps(result), content_type='application/json')

async def logs(request):
    DockerContainer.refresh_containers()
    body = await request.json()
    container_id = body.get('id', None)
    if not container_id: return web.Response(text='container id is necessary')
    tail_count = body.get('tail', 100)
    container = DockerContainer.containers[container_id]
    logs_content = container.logs(tail_count)
    return web.Response(text=json.dumps(dict(content=logs_content.decode())), content_type='application/json')

async def execute(request):
    DockerContainer.refresh_containers()
    body = await request.json()
    container_id = body.get('id', None)
    if not container_id: return web.Response(text='container id is necessary')
    command = body.get('command', None)
    if not command: return web.Response(text='command is necessary')
    container = DockerContainer.containers[container_id]
    logs_content = container.exec(command)
    print(logs_content)
    return web.Response(text=json.dumps(dict(content=logs_content.decode())), content_type='application/json')

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/', list_latest)
    app.router.add_post('/logs', logs)
    app.router.add_post('/exec', execute)
    web.run_app(app)