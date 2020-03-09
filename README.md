## Hyperledger Fabric Simple Manager

### agh

component agent

```bash
# list running container
curl localhost:8080

# logs running container
curl -d '{"id":"75ea589dc330d5c25b7b56f564db800be34311bbc642f2c0c200ab2df6693d49","tail":500}' -H "Content-Type: application/json" -X POST http://localhost:8080/logs

# exec command in running
curl -d '{"id":"ffbf8723ff06e13c87f1c44057b77dbd22c9ab28b56b51c882480236d26422af","command":"peer channel getinfo -c mychannel"}' -H "Content-Type: application/json" -X POST http://localhost:8080/exec

```

### agM

master of compnent agents

```bash

# list components containers
curl -d '{"uris":["localhost:8080"]}' -H "Content-Type: application/json" -X POST http://localhost:8080/

# list components containers logs 
curl -d '{"logs":[{"localhost:8080":[<id>, 100]}]}' -H "Content-Type: application/json" -X POST http://localhost:8081/logs

# execute commands in docker containers
curl -d '{"logs":[{"localhost:8080":[<id>, <command>]}]}' -H "Content-Type: application/json" -X POST http://localhost:8081/logs

```

## client

UI for administrator