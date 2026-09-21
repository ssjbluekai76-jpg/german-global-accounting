(function () {
"use strict";
var DICT = window.I18N;
var STORAGE_KEY = "gga_lang";
var DEFAULT_LANG = "en";
var LANGS = ["en", "de", "ar"];
var WA_NUMBER = "971509302885";
var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function t(key, lang) {
var d = DICT[lang];
if (d && typeof d[key] === "string") return d[key];
if (DICT.en && typeof DICT.en[key] === "string") {
if (window.console) console.warn("[i18n] missing " + lang + "." + key + " — fell back to English");
return DICT.en[key];
}
if (window.console) console.warn("[i18n] unknown key: " + key);
return "";
}
function normalise(lang) {
return LANGS.indexOf(lang) > -1 ? lang : DEFAULT_LANG;
}
function readStoredLang() {
var m = /[?&]lang=([a-z]{2})/i.exec(window.location.search);
if (m && LANGS.indexOf(m[1].toLowerCase()) > -1) return m[1].toLowerCase();
try {
var v = localStorage.getItem(STORAGE_KEY);
if (v && LANGS.indexOf(v) > -1) return v;
} catch (e) { /* private mode — fall through */ }
var nav = (navigator.language || "").slice(0, 2).toLowerCase();
return normalise(nav);
}
function storeLang(lang) {
try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* ignore */ }
}
function updateWhatsAppLinks(lang) {
document.querySelectorAll("[data-wa]").forEach(function (el) {
var key = el.getAttribute("data-wa") === "price" ? "wa_msg_price" : "wa_msg_consult";
el.setAttribute("href", "https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(t(key, lang)));
});
}
function paint(lang) {
document.querySelectorAll("[data-i18n]").forEach(function (el) {
var key = el.getAttribute("data-i18n");
var value = t(key, lang);
var attr = el.getAttribute("data-i18n-attr");
if (attr) {
attr.split(",").forEach(function (a) { el.setAttribute(a.trim(), value); });
} else {
el.innerHTML = value;
}
});
var titleKey = document.documentElement.getAttribute("data-title-key");
var descKey = document.documentElement.getAttribute("data-desc-key");
if (titleKey) document.title = t(titleKey, lang);
if (descKey) {
var meta = document.querySelector('meta[name="description"]');
if (meta) meta.setAttribute("content", t(descKey, lang));
}
updateWhatsAppLinks(lang);
}
function loadArabicFont(lang) {
if (lang !== "ar" || document.getElementById("font-readex")) return;
var l = document.createElement("link");
l.id = "font-readex";
l.rel = "stylesheet";
l.href = "https://fonts.googleapis.com/css2?family=Readex+Pro:wght@300;400;500;600&display=swap";
document.head.appendChild(l);
}
var swapTimer = null;
function applyLanguage(lang, opts) {
lang = normalise(lang);
var meta = DICT[lang];
var root = document.documentElement;
var initial = !!(opts && opts.initial);
var animate = !initial && !reduceMotion && root.getAttribute("lang") !== lang;
function commit() {
loadArabicFont(lang);
root.setAttribute("lang", lang);
root.setAttribute("dir", meta.dir);
paint(lang);
syncSwitchers(lang);
}
window.clearTimeout(swapTimer);
root.classList.remove("lang-swapping", "lang-arriving");
if (animate) {
document.querySelectorAll("[data-i18n]").forEach(function (el) {
var y = el.getBoundingClientRect().top;
el.style.setProperty("--sd", Math.round(Math.min(Math.max(y, 0) / window.innerHeight, 1) * 90) + "ms");
});
root.classList.add("lang-swapping");
swapTimer = window.setTimeout(function () {
commit();
root.classList.remove("lang-swapping");
root.classList.add("lang-arriving");
swapTimer = window.setTimeout(function () {
root.classList.remove("lang-arriving");
document.querySelectorAll("[data-i18n]").forEach(function (el) { el.style.removeProperty("--sd"); });
}, 700);
}, 250);
} else {
commit();
}
storeLang(lang);
if (!initial) {
try {
var url = new URL(window.location.href);
url.searchParams.set("lang", lang);
window.history.replaceState(null, "", url);
} catch (e) { /* older browsers — harmless */ }
}
}
function syncSwitchers(lang) {
document.querySelectorAll("[data-lang]").forEach(function (btn) {
btn.setAttribute("aria-current", btn.getAttribute("data-lang") === lang ? "true" : "false");
});
movePill();
}
var pillReady = false;
function movePill() {
var wrap = document.querySelector(".lang");
if (!wrap) return;
var pill = wrap.querySelector(".lang-pill");
var active = wrap.querySelector('[aria-current="true"]');
if (!pill || !active || !active.offsetWidth) return;   // hidden at this breakpoint
pill.style.setProperty("--pw", active.offsetWidth + "px");
pill.style.setProperty("--px", active.offsetLeft + "px");
if (!pillReady) {
window.requestAnimationFrame(function () { wrap.classList.add("is-ready"); });
pillReady = true;
}
}
function initLangSeg() {
window.addEventListener("resize", movePill);
if (document.fonts) {
if (document.fonts.ready) document.fonts.ready.then(movePill);
if (document.fonts.addEventListener) document.fonts.addEventListener("loadingdone", movePill);
}
}
document.addEventListener("click", function (e) {
var btn = e.target.closest ? e.target.closest("[data-lang]") : null;
if (!btn) return;
e.preventDefault();
applyLanguage(btn.getAttribute("data-lang"));
closeNav();
});
var navToggle = document.getElementById("navToggle");
var mobileNav = document.getElementById("mobileNav");
var navScrim = document.getElementById("navScrim");
var navClose = document.getElementById("navClose");
var lastFocus = null;
function openNav() {
if (!mobileNav) return;
lastFocus = document.activeElement;
document.body.classList.add("nav-open");
document.body.style.overflow = "hidden";
if (navToggle) navToggle.setAttribute("aria-expanded", "true");
mobileNav.setAttribute("aria-hidden", "false");
var first = mobileNav.querySelector("a, button");
if (first) first.focus();
}
function closeNav() {
if (!mobileNav || !document.body.classList.contains("nav-open")) return;
document.body.classList.remove("nav-open");
document.body.style.overflow = "";
if (navToggle) navToggle.setAttribute("aria-expanded", "false");
mobileNav.setAttribute("aria-hidden", "true");
if (lastFocus && lastFocus.focus) lastFocus.focus();
}
if (navToggle) {
navToggle.addEventListener("click", function () {
document.body.classList.contains("nav-open") ? closeNav() : openNav();
});
}
if (navClose) navClose.addEventListener("click", closeNav);
if (navScrim) navScrim.addEventListener("click", closeNav);
if (mobileNav) {
mobileNav.querySelectorAll("a").forEach(function (a) {
a.addEventListener("click", closeNav);
});
}
document.addEventListener("keydown", function (e) {
if (e.key === "Escape") closeNav();
});
window.matchMedia("(min-width: 1080px)").addEventListener("change", function (ev) {
if (ev.matches) closeNav();
});
var header = document.getElementById("siteHeader");
var toTop = document.getElementById("toTop");
var ringFill = toTop ? toTop.querySelector(".tt-fill") : null;
var processGrid = document.querySelector(".process-grid");
var beam = processGrid ? processGrid.querySelector(".process-beam") : null;
var processSteps = processGrid ? Array.prototype.slice.call(processGrid.querySelectorAll(".process-step")) : [];
var rail = null;   // measured geometry of the process rail
function measureRail() {
if (!processGrid || processSteps.length < 2) return;
var g = processGrid.getBoundingClientRect();
var first = processSteps[0].querySelector(".n").getBoundingClientRect();
var last = processSteps[processSteps.length - 1].querySelector(".n").getBoundingClientRect();
var top = first.top - g.top + first.height / 2;
var bottom = last.top - g.top + last.height / 2;
rail = { top: top, height: bottom - top, x: first.left - g.left + first.width / 2 };
processGrid.style.setProperty("--rail-top", top + "px");
processGrid.style.setProperty("--rail-h", rail.height + "px");
processGrid.style.setProperty("--rail-x", rail.x + "px");
}
var cachedMax = -1;
function docMax() {
if (cachedMax < 0) cachedMax = document.documentElement.scrollHeight - window.innerHeight;
return cachedMax;
}
window.addEventListener("resize", function () { cachedMax = -1; });
window.addEventListener("load", function () { cachedMax = -1; onScroll(); });
if (window.ResizeObserver) new ResizeObserver(function () { cachedMax = -1; }).observe(document.body);
function updateScrollState() {
var y = window.scrollY;
if (header) header.classList.toggle("is-scrolled", y > 8);
if (toTop) {
var max = docMax();
var p = max > 0 ? Math.min(y / max, 1) : 0;
if (ringFill) ringFill.style.strokeDashoffset = String(100 - p * 100);
toTop.classList.toggle("is-on", y > 520);
}
if (beam && rail) {
var g = processGrid.getBoundingClientRect();
var mark = window.innerHeight * 0.62;            // the "reading line"
var travelled = Math.min(Math.max(mark - (g.top + rail.top), 0), rail.height);
beam.style.setProperty("--beam", travelled + "px");
processSteps.forEach(function (step) {
var n = step.querySelector(".n").getBoundingClientRect();
step.classList.toggle("is-lit", n.top + n.height / 2 < mark);
});
}
}
var scrollTick = false;
function onScroll() {
if (scrollTick) return;
scrollTick = true;
window.requestAnimationFrame(function () { scrollTick = false; updateScrollState(); });
}
window.addEventListener("scroll", onScroll, { passive: true });
window.addEventListener("resize", function () { measureRail(); onScroll(); });
if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { measureRail(); onScroll(); });
measureRail();
updateScrollState();
if (toTop) {
toTop.addEventListener("click", function () {
window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
});
}
(function reveals() {
var els = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
if (!els.length) return;
function finish(el) { el.classList.add("is-done"); el.style.removeProperty("--rd"); }
function showAll() { els.forEach(function (el) { el.classList.add("is-visible"); finish(el); }); }
if (reduceMotion || !("IntersectionObserver" in window)) { showAll(); return; }
var observerAlive = false;
var io = new IntersectionObserver(function (entries) {
observerAlive = true;                              // it called back at least once
var firing = entries.filter(function (e) { return e.isIntersecting; });
firing.forEach(function (entry, i) {
var el = entry.target;
el.style.setProperty("--rd", Math.min(i * 80, 480) + "ms");
el.classList.add("is-visible");
io.unobserve(el);
var done = false;
var end = function () { if (!done) { done = true; finish(el); } };
el.addEventListener("transitionend", function onEnd(ev) {
if (ev.target === el && ev.propertyName === "opacity") { el.removeEventListener("transitionend", onEnd); end(); }
});
window.setTimeout(end, 1900 + i * 80);         // safety net if transitionend never fires
});
}, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
els.forEach(function (el) { io.observe(el); });
window.setTimeout(function () { if (!observerAlive) showAll(); }, 3000);
})();
(function polish() {
var heads = Array.prototype.slice.call(document.querySelectorAll(
".section-head h2, .about-col h2, .split h2, .cta-band h2, .quote-panel h2"));
if (!heads.length) return;
heads.forEach(function (h) { h.classList.add("polish"); });
if (reduceMotion || !("IntersectionObserver" in window)) return;
var io = new IntersectionObserver(function (entries) {
entries.forEach(function (e) {
if (e.isIntersecting) { e.target.classList.add("is-polished"); io.unobserve(e.target); }
});
}, { threshold: 0.6 });
heads.forEach(function (h) { io.observe(h); });
})();
(function pointerEffects() {
if (reduceMotion || !window.matchMedia("(hover: hover)").matches) return;
var glareSel = ".card, .place-card, .factor, .addl-card, .goal-card, .why-item, .svc-detail, .quote-panel";
document.querySelectorAll(glareSel).forEach(function (el) {
var tilt = el.classList.contains("card");
el.addEventListener("pointermove", function (e) {
var r = el.getBoundingClientRect();
var x = (e.clientX - r.left) / r.width;
var y = (e.clientY - r.top) / r.height;
el.style.setProperty("--mx", (x * 100).toFixed(1) + "%");
el.style.setProperty("--my", (y * 100).toFixed(1) + "%");
if (tilt) {
el.style.setProperty("--ry", ((x - 0.5) * 7).toFixed(2) + "deg");
el.style.setProperty("--rx", ((0.5 - y) * 7).toFixed(2) + "deg");
}
});
if (tilt) {
el.addEventListener("pointerleave", function () {
el.style.setProperty("--rx", "0deg");
el.style.setProperty("--ry", "0deg");
});
}
});
})();
(function scrollLit() {
if (reduceMotion || !("IntersectionObserver" in window)) return;
var mq = window.matchMedia("(hover: none), (max-width: 899px)");
var els = Array.prototype.slice.call(document.querySelectorAll(
".card, .why-item, .process-step, .addl-card, .factor, .place-card, .chips li, " +
".svc-detail, .split-figure, .pricing-feature, .goal-card, .quote-panel, .contact-row, .map-link"));
if (!els.length) return;
var io = null;
function start() {
if (io) return;
io = new IntersectionObserver(function (entries) {
entries.forEach(function (e) { e.target.classList.toggle("scroll-lit", e.isIntersecting); });
}, { rootMargin: "-36% 0px -36% 0px", threshold: 0 });
els.forEach(function (el) { io.observe(el); });
}
function stop() {
if (!io) return;
io.disconnect(); io = null;
els.forEach(function (el) { el.classList.remove("scroll-lit"); });
}
function sync() { mq.matches ? start() : stop(); }
sync();
if (mq.addEventListener) mq.addEventListener("change", sync);
})();
(function contactForm() {
var form = document.getElementById("contactForm");
if (!form) return;
var status = document.getElementById("formStatus");
var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
function lang() { return normalise(document.documentElement.getAttribute("lang")); }
function setError(field, hasError) {
var f = field.closest(".field");
if (hasError) {
f.classList.remove("has-error");
void f.offsetWidth;
f.classList.add("has-error");
} else {
f.classList.remove("has-error");
}
}
function validate() {
var ok = true;
var name = form.elements.name;
var email = form.elements.email;
var message = form.elements.message;
setError(name, !name.value.trim());
if (!name.value.trim()) ok = false;
setError(email, !emailRe.test(email.value.trim()));
if (!emailRe.test(email.value.trim())) ok = false;
setError(message, !message.value.trim());
if (!message.value.trim()) ok = false;
if (!ok) {
var firstBad = form.querySelector(".field.has-error input, .field.has-error textarea");
if (firstBad) firstBad.focus();
}
return ok;
}
function compose() {
var l = lang();
var f = form.elements;
var topicSelect = f.topic;
var topicLabel = topicSelect.value
? topicSelect.options[topicSelect.selectedIndex].textContent.trim()
: "";
var lines = [];
lines.push(t("form_name", l) + ": " + f.name.value.trim());
lines.push(t("form_email", l) + ": " + f.email.value.trim());
if (f.company.value.trim()) lines.push(t("form_company", l) + ": " + f.company.value.trim());
if (topicLabel) lines.push(t("form_topic", l) + ": " + topicLabel);
lines.push("");
lines.push(f.message.value.trim());
return {
subject: t("contact_form_h2", l) + " — " + f.name.value.trim(),
body: lines.join("\n")
};
}
function announce(key) {
if (!status) return;
status.innerHTML = '<span class="tick" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></span><span class="msg"></span>';
status.querySelector(".msg").textContent = t(key, lang());
status.classList.remove("is-visible");
void status.offsetWidth;
status.classList.add("is-visible");
}
form.addEventListener("submit", function (e) { e.preventDefault(); });
var sendWa = document.getElementById("sendWhatsApp");
if (sendWa) {
sendWa.addEventListener("click", function () {
if (!validate()) return;
var m = compose();
announce("form_success_wa");
window.open("https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(m.body), "_blank", "noopener");
});
}
form.addEventListener("input", function (e) {
var field = e.target.closest(".field");
if (field && field.classList.contains("has-error")) field.classList.remove("has-error");
});
})();
document.querySelectorAll("[data-year]").forEach(function (el) {
el.textContent = new Date().getFullYear();
});
initLangSeg();
applyLanguage(readStoredLang(), { initial: true });
window.setTimeout(function () { document.documentElement.classList.add("is-settled"); }, 4200);
})();
