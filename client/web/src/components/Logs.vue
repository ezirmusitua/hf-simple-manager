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
      <input v-model="tail" placeholder="tail count" />
      <button @click="showLogs">Refresh</button>
    </div>
    <article class="output logs">
      <code class="result" v-for="(log, i) in logs" :key="i">{{log}}</code>
    </article>
  </section>
</template>

<script>
import * as axios from "axios";

const APIs = {
  fetchContainerLogs: async (id, host, tail = 100) => {
    const { data } = await axios.post(
      `http://172.30.4.121:3000/container/${id}/logs`,
      {
        host,
        tail
      }
    );
    return data;
  }
};

export default {
  name: "Logs",
  props: ["target"],
  data() {
    return {
      loading: false,
      tail: 100,
      container: null,
      logs: []
    };
  },
  created() {
    if (!this.container || this.container.id !== this.target.id) {
      this.container = { ...this.target };
      this.logs = [];
      this.loading = false;
      this.showLogs();
    }
  },
  methods: {
    async showLogs() {
      if (this.loading) return;
      this.loading = true;
      const { content } = await APIs.fetchContainerLogs(
        this.container.id,
        this.container.host,
        this.tail
      );
      this.logs = content.split("\n");
      this.loading = false;
    }
  }
};
</script>