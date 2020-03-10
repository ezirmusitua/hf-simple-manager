<style scoped>
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
    <h3>Logs</h3>
    <div class="command input-target">
      <input v-model="command" />
      <button @click="execute">Execute</button>
    </div>
    <article class="output logs">
      <code class="result" v-for="(log, i) in logs" :key="i">{{log}}</code>
    </article>
  </section>
</template>

<script>
import * as axios from "axios";

const APIs = {
  executeContainerCommand: async (
    id,
    host,
    command
  ) => {
    const {
      data
    } = await axios.post(`http://172.30.4.121:3000/container/${id}/exec`, {
      host,
      command
    });
    return data;
  },
};

export default {
  name: "Logs",
  props: ["target"],
  data() {
    return {
      loading: false,
      container: null,
      logs: [],
      command: "peer channel getinfo -c mychannel"
    };
  },
  created() {
    if (!this.container || this.container.id !== this.target.id) {
      this.container = {...this.target};
      this.command = "peer channel getinfo -c mychannel"
      this.logs = [];
      this.loading = false;
    }
  },
  methods: {
    async execute() {
      if (this.loading) return;
      if (!this.container) {
        alert("No target selected");
        return;
      }
      if (!this.command) {
        alert("No command input");
        return;
      }
      this.loading = true;
      const { content } = await APIs.executeContainerCommand(
        this.container.id,
        this.container.host,
        this.command
      );
      this.logs = content.split("\n");
      this.loading = false;
    }
  }
};
</script>