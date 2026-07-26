import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { refreshCatalystAuth } from "./services/auth";
import "./index.css";

async function boot() {
  await refreshCatalystAuth();
  createApp(App).use(router).mount("#app");
}

void boot();
