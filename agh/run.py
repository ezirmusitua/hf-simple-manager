# -*- utf-8 -*-
import os
import json
import subprocess
from aiohttp import web
import docker

working_dir = '/' + os.path.join('home', 'jz', 'Projects', 'fabric-samples')
configtxlator_bin_path = os.path.join(
    working_dir, os.path.join('bin', 'configtxlator'))


def block_pb_2_json(pbfile, jsonfile):
    os.system(configtxlator_bin_path + ' proto_decode --input ' +
              pbfile + ' --type common.Block > ' + jsonfile)

def envelope_json_2_pb(jsonfile, pbfile):
    subprocess.run([
        configtxlator_bin_path,
        'proto_decode',
        '--input',
        jsonfile,
        '--type'
        'common.Envelope',
        '--output',
        pbfile
    ])


class DockerContainer:

    docker_client = docker.from_env()
    containers = dict()

    def __init__(self, container_info):
        self.id = container_info.id
        self.name = container_info.name
        self.image = container_info.image
        self.status = container_info.status
        self._container = container_info

    def logs(self, tail=100):
        logs = self._container.logs()
        return logs

    def exec(self, command):
        if not command:
            raise Exception("command is necessary")
        code, logs = self._container.exec_run(command)
        return logs

    def to_json(self):
        return dict(
            id=self.id,
            name=self.name,
            image=str(self.image),
            status=self.status
        )

    @staticmethod
    def load_containers(refresh=False):
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


async def validate_body(request, required=[]):
    body = await request.json()
    ret = dict()
    for field in required:
        value = body.get(field, None)
        if not value:
            return web.Response(text=field + ' is necessary')
        ret[field] = value
    return ret


async def list_latest(request):
    result = list()
    for container in DockerContainer.refresh_containers():
        result.append(container.to_json())
    return web.Response(text=json.dumps(dict(items=result)), content_type='application/json')


async def logs(request):
    DockerContainer.refresh_containers()
    body = await validate_body(request, ['id', 'tail'])
    container = DockerContainer.containers[body['id']]
    logs_content = container.logs(body['tail'])
    return web.Response(text=json.dumps(dict(content=logs_content.decode())), content_type='application/json')


async def execute(request):
    DockerContainer.refresh_containers()
    body = await validate_body(request, ['id', 'command'])
    container = DockerContainer.containers[body['id']]
    logs_content = container.exec(body['command'])
    return web.Response(text=json.dumps(dict(content=logs_content.decode())), content_type='application/json')


async def get_channel_config(request):
    DockerContainer.refresh_containers()
    body = await validate_body(request, ['id', 'channel'])
    container = DockerContainer.containers[body['id']]
    command = ('peer channel fetch config '
               + 'channel-artifacts/{channel}.config.block -c {channel}'
               #    + '--tls -o localhost:8050 '
               #    + '--cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/msp/tlscacerts/tlsca.example.com-cert.pem'
               ).format(channel=body['channel'])
    logs_content = container.exec(command)
    block_pb_path = os.path.join(
        working_dir,
        'first-network',
        'channel-artifacts',
        body['channel'] + '.config.block'
    )
    block_json_path = os.path.join(
        working_dir,
        'first-network',
        'channel-artifacts',
        body['channel'] + '.config.json'
    )
    block_pb_2_json(
        block_pb_path,
        block_json_path
    )
    with open(block_json_path, 'r') as rf:
        return web.Response(
            text=json.dumps(
                dict(
                    content=logs_content.decode(),
                    config=json.load(rf)['data']['data'][0]['payload']['data']['config']['channel_group']
                )
            ),
            content_type='application/json'
        )


if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/', list_latest)
    app.router.add_post('/logs', logs)
    app.router.add_post('/exec', execute)
    app.router.add_post('/channel-config', get_channel_config)
    web.run_app(app, host='0.0.0.0', port=8888)
