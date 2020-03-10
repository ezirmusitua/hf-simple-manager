<style>
body {
  margin: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  background-color: #efefef;
  height: 100vh;
}

#app p {
  margin: 0;
}

.content {
  min-width: 1280px;
  margin: 0 auto;
}
.content > section {
  padding: 20px 24px;
  margin-bottom: 24px;
  border: 1px dotted grey;
}
.container-item {
  position: relative;
  box-sizing: border-box;
  cursor: pointer;
  border: 1px solid #0a0a0a;
  border-radius: 4px;
  padding: 8px 16px;
  margin: 2px 0;
  display: flex;
  width: 100%;
  justify-content: space-between;
}
.container-item p {
  flex-basis: 25%;
}
.container-item .selected {
  position: absolute;
  left: 0;
  top: 0;
  font-size: 20px;
  font-weight: bold;
  color: red;
}
.container-item:hover {
  background-color: grey;
}

.input-container {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  height: 32px;
}
.input-container input {
  box-sizing: border-box;
  flex-basis: 70%;
  height: 100%;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
  border-right: 0;
}
.input-container button {
  flex: 1;
  height: 100%;
  border-left: 0;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  cursor: pointer;
}
.output {
  display: flex;
  flex-direction: column;
  padding: 16px 4px;
  min-height: 120px;
}
.output .result {
  text-align: start;
  line-break: anywhere;
  color: #f0f0f0;
  background-color: #0f0f0f;
  padding: 2px 4px;
  line-height: 1.2;
}

.config textarea {
  min-height: 1000px;
}

.config textarea:disabled {
  background-color: #0f0f0f;
  border: 0;
}

.config-compare-editor {
  display: flex;
  justify-content: space-between;
}

.config-compare-editor article {
  flex-basis: 49%;
}

</style>

<template>
  <div id="app">
    <div class="content">
      <section>
        <h3>Containers</h3>
        <article>
          <section
            class="container-item"
            v-for="container in containers"
            :key="container.id"
            @click="() => onContainerSelect(container)"
          >
            <div
              v-if="current.container && container.id === current.container.id"
              class="selected"
            >*</div>
            <p>{{container.id.slice(0, 6)}}</p>
            <p>{{container.name}}</p>
            <p>{{container.status}}</p>
            <!-- <p>{{container.image}}</p> -->
            <p>{{container.host}}</p>
          </section>
        </article>
      </section>
      <section>
        <h3>Command + Shortcuts</h3>
        <div class="command input-container">
          <input v-model="current.command" />
          <button @click="() => execute()">Execute</button>
        </div>
        <div class="shortcuts input-container">
          <input v-model="shortcuts.channel" />
          <button @click="getChannelConfig">Get Channel Config</button>
        </div>
      </section>
      <section>
        <h3>Config</h3>
        <button @click="updateChannelConfig">Update Config</button>
        <div class="config-compare-editor">
        <article class="output config">
          <textarea class="result" disabled="true" v-model="shortcuts.config"></textarea>
        </article>
        <article class="output config">
          <textarea class="result" :disabled="!shortcuts.newConfig" v-model="shortcuts.newConfig"></textarea>
        </article>
        </div>
      </section>
      <section>
        <h3>Logs</h3>
        <article class="output logs">
          <code class="result" v-for="(log, i) in current.logs" :key="i">{{log}}</code>
        </article>
      </section>
    </div>
  </div>
</template>

<script>
import * as axios from "axios";

const APIs = {
  listContainers: async () => {
    const { data } = await axios.post("http://172.30.4.121:3000/container", {
      hosts: ["172.30.4.121"]
    });
    return data;
  },
  fetchContainerLogs: async (id, host, tail = 100) => {
    const {
      data
    } = await axios.post(`http://172.30.4.121:3000/container/${id}/logs`, {
      host,
      tail
    });
    return data;
  },
  executeContainerCommand: async (
    id,
    host,
    command = "peer channel getinfo -c mychannel"
  ) => {
    const {
      data
    } = await axios.post(`http://172.30.4.121:3000/container/${id}/exec`, {
      host,
      command
    });
    return data;
  },
  getChannelConfig: async (
    id,
    host,
    channel
  ) => {
    const {
      data
    } = await axios.post(`http://172.30.4.121:3000/container/${id}/get-channel-config`, {
      host,
      channel
    });
    return data;
  },
  updateChannelConfig: async (
    id,
    host,
    channel,
    envelope
  ) => {
    const {
      data
    } = await axios.put(`http://172.30.4.121:3000/container/${id}/update-channel-config`, {
      host,
      channel,
      envelope
    });
    return data;
  }
};

export default {
  name: "App",
  components: {},
  filters: {},
  methods: {
    onContainerSelect(item) {
      alert("Select");
      this.current = {
        container: item,
        comamnd: "",
        logs: ""
      };
      this.logs();
    },
    async list() {
      if (this.loading) return;
      this.loading = true;
      const { items } = await APIs.listContainers();
      this.containers = items;
      this.current.container = items[0];
      this.loading = false;
    },
    async logs(tail = 100) {
      if (this.loading) return;
      this.loading = true;
      const { content } = await APIs.fetchContainerLogs(
        this.current.container.id,
        this.current.container.host,
        tail
      );
      this.current.logs = content.split("\n");
      this.loading = false;
    },
    async execute() {
      if (this.loading) return;
      if (!this.current.container) {
        alert("No container selected");
        return;
      }
      if (!this.current.command) {
        alert("No command input");
        return;
      }
      this.loading = true;
      const { content } = await APIs.executeContainerCommand(
        this.current.container.id,
        this.current.container.host,
        this.current.container.command
      );
      this.current.logs = content.split("\n");
      this.loading = false;
    },
    async getChannelConfig() {
      if (this.loading) return;
      if (!this.current.container) {
        alert("No container selected");
        return;
      }
      this.loading = true;
      const { content, config } = await APIs.getChannelConfig(
        this.current.container.id,
        this.current.container.host,
        this.shortcuts.channel
      );
      this.current.logs = content.split("\n");
      this.shortcuts.config = JSON.stringify(config, null, 2); 
      this.shortcuts.newConfig = this.shortcuts.config;
      this.loading = false;
    },
    async updateChannelConfig() {
      if (this.loading) return;
      if (!this.current.container) {
        alert("No container selected");
        return;
      }
      this.loading = true;
      const envelope = {
        payload: {
          header: {
            channel_header: {
              channel_id: this.shortcuts.channel,
              type: 2
            }
          },
          data: {
              config_update: {
                channel_id: this.shortcuts.channel,
                isolated_data: {},
                read_set: JSON.parse(this.shortcuts.config),
                write_set: JSON.parse(this.shortcuts.newConfig),
              }
          }
        }
      }
      const { content, config } = await APIs.updateChannelConfig(
        this.current.container.id,
        this.current.container.host,
        this.shortcuts.channel,
        envelope
      );
      this.current.logs = content.split("\n");
      this.shortcuts.config = JSON.stringify(config, null, 2); 
      this.shortcuts.newConfig = this.shortcuts.config;
      this.loading = false;
    }
  },
  data() {
    return {
      loading: false,
      current: {
        container: null,
        command: "peer channel getinfo -c mychannel",
        logs: ""
      },
      shortcuts: {
        channel: ""
      },
      containers: []
    };
  },
  mounted() {
    // const demoLogsReturn = ```{"content": "\u001b[34m2020-03-09 10:27:14.123 UTC [localconfig] completeInitialization -> INFO 001\u001b[0m Kafka.Version unset, setting to 0.10.2.0\n\u001b[34m2020-03-09 10:27:14.133 UTC [orderer.common.server] prettyPrintStruct -> INFO 002\u001b[0m Orderer config values:\n\tGeneral.LedgerType = \"file\"\n\tGeneral.ListenAddress = \"0.0.0.0\"\n\tGeneral.ListenPort = 7050\n\tGeneral.TLS.Enabled = true\n\tGeneral.TLS.PrivateKey = \"/var/hyperledger/orderer/tls/server.key\"\n\tGeneral.TLS.Certificate = \"/var/hyperledger/orderer/tls/server.crt\"\n\tGeneral.TLS.RootCAs = [/var/hyperledger/orderer/tls/ca.crt]\n\tGeneral.TLS.ClientAuthRequired = false\n\tGeneral.TLS.ClientRootCAs = []\n\tGeneral.Cluster.ListenAddress = \"\"\n\tGeneral.Cluster.ListenPort = 0\n\tGeneral.Cluster.ServerCertificate = \"\"\n\tGeneral.Cluster.ServerPrivateKey = \"\"\n\tGeneral.Cluster.ClientCertificate = \"/var/hyperledger/orderer/tls/server.crt\"\n\tGeneral.Cluster.ClientPrivateKey = \"/var/hyperledger/orderer/tls/server.key\"\n\tGeneral.Cluster.RootCAs = [/var/hyperledger/orderer/tls/ca.crt]\n\tGeneral.Cluster.DialTimeout = 5s\n\tGeneral.Cluster.RPCTimeout = 7s\n\tGeneral.Cluster.ReplicationBufferSize = 20971520\n\tGeneral.Cluster.ReplicationPullTimeout = 5s\n\tGeneral.Cluster.ReplicationRetryTimeout = 5s\n\tGeneral.Cluster.ReplicationBackgroundRefreshInterval = 5m0s\n\tGeneral.Cluster.ReplicationMaxRetries = 12\n\tGeneral.Cluster.SendBufferSize = 10\n\tGeneral.Cluster.CertExpirationWarningThreshold = 168h0m0s\n\tGeneral.Cluster.TLSHandshakeTimeShift = 0s\n\tGeneral.Keepalive.ServerMinInterval = 1m0s\n\tGeneral.Keepalive.ServerInterval = 2h0m0s\n\tGeneral.Keepalive.ServerTimeout = 20s\n\tGeneral.ConnectionTimeout = 0s\n\tGeneral.GenesisMethod = \"file\"\n\tGeneral.GenesisProfile = \"SampleInsecureSolo\"\n\tGeneral.SystemChannel = \"test-system-channel-name\"\n\tGeneral.GenesisFile = \"/var/hyperledger/orderer/orderer.genesis.block\"\n\tGeneral.Profile.Enabled = false\n\tGeneral.Profile.Address = \"0.0.0.0:6060\"\n\tGeneral.LocalMSPDir = \"/var/hyperledger/orderer/msp\"\n\tGeneral.LocalMSPID = \"OrdererMSP\"\n\tGeneral.BCCSP.ProviderName = \"SW\"\n\tGeneral.BCCSP.SwOpts.SecLevel = 256\n\tGeneral.BCCSP.SwOpts.HashFamily = \"SHA2\"\n\tGeneral.BCCSP.SwOpts.Ephemeral = false\n\tGeneral.BCCSP.SwOpts.FileKeystore.KeyStorePath = \"/var/hyperledger/orderer/msp/keystore\"\n\tGeneral.BCCSP.SwOpts.DummyKeystore =\n\tGeneral.BCCSP.SwOpts.InmemKeystore =\n\tGeneral.BCCSP.PluginOpts =\n\tGeneral.Authentication.TimeWindow = 15m0s\n\tGeneral.Authentication.NoExpirationChecks = false\n\tFileLedger.Location = \"/var/hyperledger/production/orderer\"\n\tFileLedger.Prefix = \"hyperledger-fabric-ordererledger\"\n\tRAMLedger.HistorySize = 1000\n\tKafka.Retry.ShortInterval = 5s\n\tKafka.Retry.ShortTotal = 10m0s\n\tKafka.Retry.LongInterval = 5m0s\n\tKafka.Retry.LongTotal = 12h0m0s\n\tKafka.Retry.NetworkTimeouts.DialTimeout = 10s\n\tKafka.Retry.NetworkTimeouts.ReadTimeout = 10s\n\tKafka.Retry.NetworkTimeouts.WriteTimeout = 10s\n\tKafka.Retry.Metadata.RetryMax = 3\n\tKafka.Retry.Metadata.RetryBackoff = 250ms\n\tKafka.Retry.Producer.RetryMax = 3\n\tKafka.Retry.Producer.RetryBackoff = 100ms\n\tKafka.Retry.Consumer.RetryBackoff = 2s\n\tKafka.Verbose = true\n\tKafka.Version = 0.10.2.0\n\tKafka.TLS.Enabled = false\n\tKafka.TLS.PrivateKey = \"\"\n\tKafka.TLS.Certificate = \"\"\n\tKafka.TLS.RootCAs = []\n\tKafka.TLS.ClientAuthRequired = false\n\tKafka.TLS.ClientRootCAs = []\n\tKafka.SASLPlain.Enabled = false\n\tKafka.SASLPlain.User = \"\"\n\tKafka.SASLPlain.Password = \"\"\n\tKafka.Topic.ReplicationFactor = 1\n\tDebug.BroadcastTraceDir = \"\"\n\tDebug.DeliverTraceDir = \"\"\n\tConsensus = map[SnapDir:/var/hyperledger/production/orderer/etcdraft/snapshot WALDir:/var/hyperledger/production/orderer/etcdraft/wal]\n\tOperations.ListenAddress = \"127.0.0.1:8443\"\n\tOperations.TLS.Enabled = false\n\tOperations.TLS.PrivateKey = \"\"\n\tOperations.TLS.Certificate = \"\"\n\tOperations.TLS.RootCAs = []\n\tOperations.TLS.ClientAuthRequired = false\n\tOperations.TLS.ClientRootCAs = []\n\tMetrics.Provider = \"disabled\"\n\tMetrics.Statsd.Network = \"udp\"\n\tMetrics.Statsd.Address = \"127.0.0.1:8125\"\n\tMetrics.Statsd.WriteInterval = 30s\n\tMetrics.Statsd.Prefix = \"\"\n\u001b[34m2020-03-09 10:27:14.154 UTC [orderer.common.server] extractSysChanLastConfig -> INFO 003\u001b[0m Bootstrapping because no existing channels\n\u001b[34m2020-03-09 10:27:14.155 UTC [orderer.common.server] initializeServerConfig -> INFO 004\u001b[0m Starting orderer with TLS enabled\n\u001b[34m2020-03-09 10:27:14.156 UTC [fsblkstorage] newBlockfileMgr -> INFO 005\u001b[0m Getting block information from block storage\n\u001b[34m2020-03-09 10:27:14.172 UTC [orderer.commmon.multichannel] Initialize -> INFO 006\u001b[0m Starting system channel 'byfn-sys-channel' with genesis block hash 91a9c447579f8a0e6d085fa7bc985f9c21261dde9a9b2b74b45ee4e8b72e0c00 and orderer type solo\n\u001b[34m2020-03-09 10:27:14.172 UTC [orderer.common.server] Start -> INFO 007\u001b[0m Starting orderer:\n Version: 1.4.4\n Commit SHA: 7917a40\n Go version: go1.12.12\n OS/Arch: linux/amd64\n\u001b[34m2020-03-09 10:27:14.172 UTC [orderer.common.server] Start -> INFO 008\u001b[0m Beginning to serve requests\n\u001b[34m2020-03-09 10:27:15.138 UTC [comm.grpc.server] 1 -> INFO 009\u001b[0m streaming call completed grpc.service=orderer.AtomicBroadcast grpc.method=Broadcast grpc.peer_address=172.18.0.7:44440 grpc.code=OK grpc.call_duration=7.140472ms\n\u001b[34m2020-03-09 10:27:15.140 UTC [fsblkstorage] newBlockfileMgr -> INFO 00a\u001b[0m Getting block information from block storage\n\u001b[34m2020-03-09 10:27:15.150 UTC [orderer.commmon.multichannel] newChain -> INFO 00b\u001b[0m Created and starting new chain mychannel\n\u001b[34m2020-03-09 10:27:15.155 UTC [comm.grpc.server] 1 -> INFO 00c\u001b[0m streaming call completed grpc.service=orderer.AtomicBroadcast grpc.method=Deliver grpc.peer_address=172.18.0.7:44438 grpc.code=OK grpc.call_duration=25.875053ms\n\u001b[33m2020-03-09 10:27:27.753 UTC [orderer.common.broadcast] Handle -> WARN 00d\u001b[0m Error reading from 172.18.0.7:44458: rpc error: code = Canceled desc = context canceled\n\u001b[33m2020-03-09 10:27:27.753 UTC [common.deliver] Handle -> WARN 00e\u001b[0m Error reading from 172.18.0.7:44456: rpc error: code = Canceled desc = context canceled\n\u001b[34m2020-03-09 10:27:27.753 UTC [comm.grpc.server] 1 -> INFO 00f\u001b[0m streaming call completed grpc.service=orderer.AtomicBroadcast grpc.method=Broadcast grpc.peer_address=172.18.0.7:44458 error=\"rpc error: code = Canceled desc = context canceled\" grpc.code=Canceled grpc.call_duration=5.44231ms\n\u001b[34m2020-03-09 10:27:27.753 UTC [comm.grpc.server] 1 -> INFO 010\u001b[0m streaming call completed grpc.service=orderer.AtomicBroadcast grpc.method=Deliver grpc.peer_address=172.18.0.7:44456 error=\"rpc error: code = Canceled desc = context canceled\" grpc.code=Canceled grpc.call_duration=7.424722ms\n\u001b[33m2020-03-09 10:27:30.835 UTC [common.deliver] Handle -> WARN 011\u001b[0m Error reading from 172.18.0.7:44474: rpc error: code = Canceled desc = context canceled\n\u001b[33m2020-03-09 10:27:30.835 UTC [orderer.common.broadcast] Handle -> WARN 012\u001b[0m Error reading from 172.18.0.7:44476: rpc error: code = Canceled desc = context canceled\n\u001b[34m2020-03-09 10:27:30.835 UTC [comm.grpc.server] 1 -> INFO 013\u001b[0m streaming call completed grpc.service=orderer.AtomicBroadcast grpc.method=Deliver grpc.peer_address=172.18.0.7:44474 error=\"rpc error: code = Canceled desc = context canceled\" grpc.code=Canceled grpc.call_duration=8.681295ms\n\u001b[34m2020-03-09 10:27:30.835 UTC [comm.grpc.server] 1 -> INFO 014\u001b[0m streaming call completed grpc.service=orderer.AtomicBroadcast grpc.method=Broadcast grpc.peer_address=172.18.0.7:44476 error=\"rpc error: code = Canceled desc = context canceled\" grpc.code=Canceled grpc.call_duration=6.037478ms\n"}```
    // console.log(demoLogsReturn)
    // console.log(JSON.parse(demoLogsReturn).content)
    console.log(axios);
    this.list();
  }
};
</script>

