import { render } from "preact";
import { App } from "./App";
import { I18nProvider } from "./lib/i18n";
import "./fonts";
import "./index.css";

const root = document.getElementById("app");
if (!root) {
  throw new Error("#app root element not found");
}
// Drop the static text for crawlers in index.html; render() would keep it.
root.textContent = "";

render(
  <I18nProvider>
    <App />
  </I18nProvider>,
  root,
);
