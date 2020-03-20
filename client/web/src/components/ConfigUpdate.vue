<style scoped>
.output {
  display: flex;
  flex-direction: column;
  padding: 16px 4px;
  min-height: 40px;
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
.input-target {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  height: 32px;
}
.input-target input {
  box-sizing: border-box;
  flex-basis: 70%;
  height: 100%;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
  border-right: 0;
}
.input-target button {
  flex: 1;
  height: 100%;
  border-left: 0;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  cursor: pointer;
}
</style>

<template>
  <section>
    <h3>Config</h3>
    <div class="command input-target">
      <input v-model="channel" />
      <button @click="getChannelConfig">Load</button>
      <button @click="updateChannelConfig">Update</button>
    </div>
    <article class="output logs">
      <code class="result" v-for="(log, i) in logs" :key="i">{{log}}</code>
    </article>
    <div class="config-compare-editor">
      <article class="output config">
        <textarea class="result" disabled="true" v-model="config"></textarea>
      </article>
      <article class="output config">
        <textarea class="result" :disabled="!newConfig" v-model="newConfig"></textarea>
      </article>
    </div>
  </section>
</template>

<script>
import * as axios from "axios";
const APIs = {
  getChannelConfig: async (id, host, channel) => {
    const { data } = await axios.post(
      `http://172.30.4.121:3000/container/${id}/get-channel-config`,
      {
        host,
        channel
      }
    );
    return data;
  },
  updateChannelConfig: async (id, host, channel, envelope) => {
    const { data } = await axios.put(
      `http://172.30.4.121:3000/container/${id}/update-channel-config`,
      {
        host,
        channel,
        envelope
      }
    );
    return data;
  }
};
export default {
  name: "ConfigUpdate",
  props: ["target"],
  created() {
    if (!this.container || this.container.id !== this.target.id) {
      this.container = { ...this.target };
      this.logs = [];
      this.config = null;
      this.newConfig = null;
      this.channel = "";
      this.loading = false;
    //   this.getChannelConfig();
    }
  },
  data() {
    return {
      loading: false,
      container: null,
      channel: "mychannel",
      logs: [],
      config: null,
      newConfig: null
    };
  },
  methods: {
    async getChannelConfig() {
      if (this.loading) return;
      if (!this.target) {
        alert("No target selected");
        return;
      }
      this.loading = true;
      const { content, config } = await APIs.getChannelConfig(
        this.container.id,
        this.container.host,
        this.channel
      );
      this.logs = content.split("\n");
      this.config = JSON.stringify(config, null, 2);
      this.newConfig = this.config;
      this.loading = false;
    },
    async updateChannelConfig() {
      if (this.loading) return;
      if (!this.container) {
        alert("No target selected");
        return;
      }
      this.loading = true;
      const envelope = {
        payload: {
          header: {
            channel_header: {
              channel_id: this.channel,
              type: 2
            }
          },
          data: {
            config_update: {
              channel_id: this.channel,
              isolated_data: {},
              read_set: JSON.parse(this.config),
              write_set: JSON.parse(this.newConfig)
            }
          }
        }
      };
      const { content, config } = await APIs.updateChannelConfig(
        this.container.id,
        this.container.host,
        this.channel,
        envelope
      );
      this.logs = content.split("\n");
      this.config = JSON.stringify(config, null, 2);
      this.newConfig = this.config;
      this.loading = false;
    }
  }
};
</script>