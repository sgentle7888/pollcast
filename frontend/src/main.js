import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router/index.js";
import "./assets/main.css";

// Diagnostics: open the page as  https://<site>/pollcast?debug=1#/surveys/NAME
// and any JavaScript error is printed on-screen (handy on phones with no console).
const DEBUG = new URLSearchParams(window.location.search).has("debug");
function showError(label, err) {
  if (!DEBUG) return;
  let box = document.getElementById("pollcast-debug");
  if (!box) {
    box = document.createElement("pre");
    box.id = "pollcast-debug";
    box.style.cssText =
      "position:fixed;left:0;right:0;bottom:0;max-height:60vh;overflow:auto;margin:0;padding:12px;" +
      "background:#7f1d1d;color:#fff;font:12px/1.4 monospace;white-space:pre-wrap;word-break:break-word;z-index:99999";
    document.body.appendChild(box);
  }
  box.textContent +=
    label + ": " + ((err && (err.stack || err.message)) || err) + "\n\n";
}
window.addEventListener("error", (e) =>
  showError("error", e.error || e.message),
);
window.addEventListener("unhandledrejection", (e) =>
  showError("promise", e.reason),
);

const app = createApp(App);
app.config.errorHandler = (err, _vm, info) => {
  console.error(err);
  showError("vue (" + info + ")", err);
};
const pinia = createPinia();

app.use(pinia);
app.use(router);
router.onError((err) => showError("router", err));
app.mount("#app");

// Load Inter without blocking rendering. If Google Fonts is slow or blocked
// (some networks/devices), the page just uses the system font fallback.
try {
  if (document.querySelector('link[href*="fonts.googleapis.com"]')) throw 0;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href =
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap";
  link.media = "print";
  link.onload = () => (link.media = "all");
  document.head.appendChild(link);
} catch {}
