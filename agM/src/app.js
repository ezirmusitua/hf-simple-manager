const Koa = require("koa");
const cors = require("@koa/cors");
const koaBody = require("koa-body");
const json = require("koa-json");
const Router = require("koa-better-router");
const axios = require("axios");

const aghPort = 18888;
const PORT = 3000;

// routes
const router = Router({ prefix: "container" });
router.loadMethods();
router.get("", (ctx, next) => {
  ctx.body = "Use POST";
  return next();
});
router.post("", async (ctx, next) => {
  const hosts = ctx.request.body.hosts;
  const promises = hosts.map(async h => {
      const url =`http://${h}:${aghPort}`; 
      const {data} = await axios.get(url);
      return data.items.map(c => ({...c, host: h}))
  });
  try {
    const result = await Promise.all(promises);
    const items = result.reduce((r, d) => {
      return r.concat(d);
    }, []);
    ctx.body = { count: items.length, items };
  } catch (e) {
    console.error(e);
    ctx.body = { error: e.toString() };
  }
  return next();
});
router.post("/:id/logs", async (ctx, next) => {
  const host = ctx.request.body.host;
  const tail = ctx.request.body.tail;
  const id = ctx.params.id;
  const url = `http://${host}:${aghPort}/logs`
  const {data} = await axios.post(url, {id, tail});
  ctx.body = data;
  return next();
});
router.post("/:id/exec", async (ctx, next) => {
  const host = ctx.request.body.host;
  const command = ctx.request.body.command;
  const id = ctx.params.id;
  const url = `http://${host}:${aghPort}/exec`
  const {data} = await axios.post(url, {id, command});
  ctx.body = data;
  return next();
});
router.post('/:id/get-channel-config', async (ctx, next) => {
  const host = ctx.request.body.host;
  const channel = ctx.request.body.channel;
  const id = ctx.params.id;
  const url = `http://${host}:${aghPort}/get-channel-config`
  const {data} = await axios.post(url, {id, channel});
  ctx.body = data;
  return next();
});
router.put('/:id/update-channel-config', async (ctx, next) => {
  const host = ctx.request.body.host;
  const channel = ctx.request.body.channel;
  const envelope = ctx.request.body.envelope;
  const id = ctx.params.id;
  const url = `http://${host}:${aghPort}/update-channel-config`
  const {data} = await axios.post(url, {id, channel, envelope});
  ctx.body = data;
  return next();
})

// app
const app = new Koa();
app.use(cors());
app.use(koaBody());
app.use(json());
app.use(router.middleware());
app.listen(PORT, () => {
  console.info(`Start listening on ${PORT}`);
});
