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
  flex-basis: 14%;
}
.container-item .selected {
  position: absolute;
  left: 0;
  top: 0;
  font-size: 20px;
  font-weight: bold;
  color: red;
}

.container-item button {
  background-color: cyan;
  border-radius: 4px;
  border: 1px solid grey;
  color: #4a4a4a;
  cursor: pointer;
}

.container-item:hover {
  background-color: grey;
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
            v-for="c in containers"
            :key="c.id"
          >
            <div
              v-if="container && container.id === c.id"
              class="selected"
            >*</div>
            <p>{{c.id.slice(0, 6)}}</p>
            <p>{{c.name}}</p>
            <p>{{c.status}}</p>
            <!-- <p>{{container.image}}</p> -->
            <p>{{c.host}}</p>
            <button @click="() => switchAction('logs', c)">logs</button>
            <button @click="() => switchAction('execute', c)">execute</button>
            <button @click="() => switchAction('config', c)">config channel</button>
          </section>
        </article>
      </section>
    </div>
    <div v-if="action === 'logs'">
      <Logs :target="container" />
    </div>
    <div v-if="action === 'execute'">
      <ExecuteCommand :target="container" />
    </div>
    <div v-if="action === 'config'">
      <ConfigUpdate :target="container" />
    </div>
  </div>
</template>

<script>

import * as axios from "axios";
import Logs from './components/Logs.vue';
import ExecuteCommand from './components/ExecuteCommand';
import ConfigUpdate from './components/ConfigUpdate';

const APIs = {
  listContainers: async () => {
    const { data } = await axios.post("http://172.30.4.121:3000/container", {
      hosts: ["10.122.144.49"]
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
  
};

export default {
  name: "App",
  components: {
    Logs,
    ExecuteCommand,
    ConfigUpdate
  },
  filters: {},
  methods: {
    async list() {
      if (this.loading) return;
      this.loading = true;
      const { items } = await APIs.listContainers();
      this.containers = items;
      this.container = items[0];
      this.loading = false;
    },
    switchAction(action, item) {
      console.log(action, item);
      this.action = "pending"; // TODO: use event bus or vuex
      setTimeout(() => {
        this.action = action;
        this.container = item;
      }, 50);
    }
  },
  data() {
    return {
      loading: false,
      container: null,
      containers: [],
      action: null
    };
  },
  created() {
    this.list();
  }
};
</script>

