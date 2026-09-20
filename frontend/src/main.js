import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router/index.js";
import "./assets/main.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.mount("#app");

// Load Inter without blocking rendering. If Google Fonts is slow or blocked
// (some networks/devices), the page just uses the system font fallback.
try {
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href =
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap";
  link.media = "print";
  link.onload = () => (link.media = "all");
  document.head.appendChild(link);
} catch {}
