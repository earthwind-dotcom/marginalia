/*
 * Behaviour tests for marginalia.html, run in a real DOM.
 *
 * The page has no build step and no framework, so these load the file as-is
 * and drive it the way a reader would. Every assertion here failed against
 * the version before the search and keyboard fixes landed, which is what
 * makes them regression tests rather than decoration.
 *
 *     npm install && node test_dom.js
 */
const fs = require("fs");
const { JSDOM } = require("jsdom");

const path = require("path");
const target = process.argv[2] || path.join(__dirname, "marginalia.html");
const body = fs.readFileSync(target, "utf8");
const page = `<!doctype html><html><head><meta charset="utf-8"></head><body>${body}</body></html>`;

const errors = [];
const dom = new JSDOM(page, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://example.test/" });
dom.virtualConsole.on("jsdomError", e => errors.push(e.message));
const { window } = dom;
const doc = window.document;

let pass = 0, fail = 0;
const t = (name, cond, extra) => cond ? (pass++, console.log("ok    " + name))
                                      : (fail++, console.log("FAIL  " + name + (extra ? "  " + extra : "")));

t("no script errors", errors.length === 0, errors.join("; "));

// --- initial route ---
const refl = doc.getElementById("view-reflections");
t("reflections visible at load", !refl.hidden);
t("other sections hidden", doc.getElementById("view-roots").hidden);

// --- tab semantics ---
const tabs = [...doc.querySelectorAll(".tab")];
t("tabs have aria-controls to a real panel",
  tabs.every(x => doc.getElementById(x.getAttribute("aria-controls"))));
t("selected tab is the only tab stop",
  tabs.filter(x => x.tabIndex === 0).length === 1,
  tabs.map(x => x.dataset.section + ":" + x.tabIndex).join(" "));
t("panel is labelled by its tab",
  refl.getAttribute("role") === "tabpanel" && refl.getAttribute("aria-labelledby") === "tab-reflections");
t("no aria-live regions remain",
  doc.querySelectorAll("[aria-live]").length === 0,
  [...doc.querySelectorAll("[aria-live]")].map(n => n.tagName).join(","));

// --- arrow-key navigation ---
const key = (el, k) => el.dispatchEvent(new window.KeyboardEvent("keydown", { key: k, bubbles: true, cancelable: true }));
tabs[0].focus();
key(tabs[0], "ArrowRight");
t("ArrowRight moves to the next section",
  !doc.getElementById("view-encounter").hidden && doc.activeElement === tabs[1],
  "active=" + (doc.activeElement && doc.activeElement.dataset.section));
key(tabs[1], "ArrowLeft");
t("ArrowLeft moves back", !refl.hidden && doc.activeElement === tabs[0]);
key(tabs[0], "End");
t("End jumps to the last tab", doc.activeElement === tabs[tabs.length - 1]);
key(tabs[tabs.length - 1], "Home");
t("Home jumps to the first tab", doc.activeElement === tabs[0]);
t("roving tabindex still holds after arrows",
  tabs.filter(x => x.tabIndex === 0).length === 1);

// --- article swapping ---
const tocItem = refl.querySelector('.toc-item[data-target="dust"]');
tocItem.dispatchEvent(new window.MouseEvent("click", { bubbles: true, cancelable: true }));
t("clicking a contents entry shows that article",
  !doc.getElementById("dust").hidden && doc.getElementById("meek").hidden);
t("hash reflects the article", window.location.hash === "#reflections/dust", window.location.hash);

// --- search, the part that was broken ---
const q = doc.getElementById("q");
const search = term => new Promise(res => {
  q.value = term;
  q.dispatchEvent(new window.Event("input", { bubbles: true }));
  setTimeout(res, 200);
});

(async () => {
  await search("meek");
  const ascii = doc.querySelectorAll("#qresults .qhit").length;
  t("ascii search finds hits", ascii > 0, "hits=" + ascii);

  // switch to Spanish so the index holds accented text
  doc.querySelector('.langpick button[data-lang="es"]')
     .dispatchEvent(new window.MouseEvent("click", { bubbles: true, cancelable: true }));
  t("language switched to es", doc.documentElement.getAttribute("data-elang") === "es");

  // words that really do live inside Spanish article bodies
  for (const [acc, plain] of [["también","tambien"], ["después","despues"],
                              ["oración","oracion"], ["Jesús","Jesus"]]) {
    await search(acc);
    const a = doc.querySelectorAll("#qresults .qhit").length;
    await search(plain);
    const b = doc.querySelectorAll("#qresults .qhit").length;
    t(`"${plain}" finds what "${acc}" finds`, a > 0 && a === b, `${acc}=${a} vs ${plain}=${b}`);
  }

  const snip = doc.querySelector("#qresults .qhit .snip");
  t("snippet highlights something", snip && snip.innerHTML.includes("<b>"), snip && snip.innerHTML.slice(0, 120));

  await search("zzzznotathing");
  t("no-match path is clean", doc.querySelectorAll("#qresults .qhit").length === 0);

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
