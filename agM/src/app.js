const Koa = require("koa");
const cors = require("@koa/cors");
const koaBody = require("koa-body");
const json = require("koa-json");
const Router = require("koa-better-router");
const axios = require("axios");

const router = Router({ prefix: "container" });
router.loadMethods();
router.get("", (ctx, next) => {
  ctx.body = "Use POST";
  return next();
});
router.post("", async (ctx, next) => {
  const hosts = ctx.request.body.hosts;
  const promises = hosts.map(async h => {
      const url =`http://${h}:8888`; 
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

// can use generator middlewares
router.post("/:id/logs", async (ctx, next) => {
  const host = ctx.request.body.host;
  const tail = ctx.request.body.tail;
  const id = ctx.params.id;
  const url = `http://${host}:8888/logs`
  const {data} = await axios.post(url, {id, tail});
  ctx.body = data;
  return next();
});

router.post("/:id/exec", async (ctx, next) => {
  this.body = `Foo Bar Baz! ${ctx.route.prefix}`;
  return next();
});

const app = new Koa();
app.use(cors());
app.use(koaBody());
app.use(json());
app.use(router.middleware());
console.debug(router.routes);
app.listen(3000, () => {
  console.info("Start listening on 3000");
});