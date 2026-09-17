// meldbar marketing pages: language, navigation, scroll effects. No network, no storage beyond
// the language preference (localStorage, shared with the app).
"use strict";

const SITE_LOCALES = { de: "de-CH", fr: "fr-CH", it: "it-CH" };
let LANG = "de";

function t(key, vars) {
  let s = (I18N_SITE[LANG] && I18N_SITE[LANG][key]) || I18N_SITE.de[key] || key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.replace("{" + k + "}", v);
  return s;
}
function applyLanguage(lang) {
  LANG = I18N_SITE[lang] ? lang : "de";
  document.documentElement.lang = LANG;
  const page = document.body.dataset.page;
  if (page && I18N_SITE.de[page + "_title"]) document.title = t(page + "_title");
  for (const el of document.querySelectorAll("[data-i18n]")) {
    const key = el.dataset.i18n;
    if (key.endsWith("_html")) el.innerHTML = t(key);
    else el.textContent = t(key);
  }
  for (const sel of document.querySelectorAll("select.lang")) sel.value = LANG;
  for (const a of document.querySelectorAll("[data-vorlage]")) a.setAttribute("href", `vorlage/meldbar-vorlage-${LANG}.xlsx`);
  try { localStorage.setItem("aeoi-lang", LANG); } catch (e) { /* ignore */ }
  document.dispatchEvent(new CustomEvent("site:language"));
}
function initialLanguage() {
  try { const s = localStorage.getItem("aeoi-lang"); if (s && I18N_SITE[s]) return s; } catch (e) { /* ignore */ }
  const nav = (navigator.language || "de").slice(0, 2).toLowerCase();
  return I18N_SITE[nav] ? nav : "de";
}
for (const sel of document.querySelectorAll("select.lang")) sel.addEventListener("change", (e) => applyLanguage(e.target.value));

applyLanguage(initialLanguage());

// mobile navigation
(function nav() {
  const burger = document.querySelector(".burger");
  const menu = document.querySelector(".mobile-nav");
  if (!burger || !menu) return;
  burger.addEventListener("click", () => {
    const open = menu.classList.toggle("open");
    burger.setAttribute("aria-expanded", String(open));
  });
  for (const a of menu.querySelectorAll("a")) a.addEventListener("click", () => menu.classList.remove("open"));
})();

// reveal on scroll
(function reveal() {
  const els = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) { els.forEach((e) => e.classList.add("in")); return; }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
  els.forEach((e) => io.observe(e));
})();

// counters: count up when visible
(function counters() {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const nodes = document.querySelectorAll("[data-count]");
  if (!nodes.length) return;
  const run = (node) => {
    const target = Number(node.dataset.count);
    if (reduced || target <= 1) { node.textContent = String(target); return; }
    const start = performance.now(), dur = 900;
    const tick = (now) => {
      const p = Math.min(1, (now - start) / dur);
      node.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if (!("IntersectionObserver" in window)) { nodes.forEach(run); return; }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { run(e.target); io.unobserve(e.target); }
  }, { threshold: 0.4 });
  nodes.forEach((n) => io.observe(n));
})();

// countdowns (days until the schema switch and the filing deadline)
(function countdown() {
  const nodes = document.querySelectorAll("[data-until]");
  if (!nodes.length) return;
  const update = () => {
    const now = new Date();
    for (const n of nodes) {
      const target = new Date(n.dataset.until + "T00:00:00");
      const days = Math.ceil((target - now) / 86400000);
      n.textContent = days > 0 ? String(days) : t("cd_done");
    }
  };
  update();
  setInterval(update, 60000);
})();

// how it works: vertical scroll drives the horizontal track (desktop); native swipe on phones
(function horizontal() {
  const wrap = document.querySelector(".how-wrap");
  const track = document.querySelector(".how-track");
  const bar = document.querySelector(".how-progress i");
  if (!wrap || !track) return;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let ticking = false;
  const render = () => {
    ticking = false;
    if (matchMedia("(max-width: 899px)").matches) { track.style.transform = ""; return; }
    const rect = wrap.getBoundingClientRect();
    const total = wrap.offsetHeight - window.innerHeight;
    const progress = Math.min(1, Math.max(0, -rect.top / total));
    const maxShift = Math.max(0, track.scrollWidth - track.parentElement.clientWidth);
    track.style.transform = `translate3d(${-progress * maxShift}px, 0, 0)`;
    if (bar) bar.style.width = `${progress * 100}%`;
  };
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(render); } };
  if (reduced) { wrap.style.height = "auto"; track.style.overflowX = "auto"; return; }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  render();
})();

// contact form: opens the visitor's mail client, sends nothing itself
(function contact() {
  const form = document.getElementById("contact-form");
  if (!form) return;
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const f = new FormData(form);
    const body = `${f.get("message") || ""}\n\n--\n${f.get("name") || ""}\n${f.get("org") || ""}`;
    location.href = `mailto:${form.dataset.to}?subject=${encodeURIComponent(t("ct_subject"))}&body=${encodeURIComponent(body)}`;
  });
})();

// hero headline: words appear one after another
(function words() {
  const h = document.querySelector(".hero-h1[data-i18n]");
  if (!h) return;
  const split = () => {
    const text = h.textContent;
    h.replaceChildren();
    text.split(" ").forEach((w, i) => {
      const s = document.createElement("span");
      s.className = "w"; s.textContent = w; s.style.animationDelay = `${i * 0.06}s`;
      h.append(s, " ");
    });
  };
  split();
  document.addEventListener("site:language", split);
})();
