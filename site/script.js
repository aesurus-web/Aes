// ---- Settings ---------------------------------------------------------
// Where enquiries go. Put your real business email here.
const CONTACT_EMAIL = "[EMAIL]";
// Optional: a form service endpoint (e.g. Formspree "https://formspree.io/f/xxxx").
// If set, the form submits there; if empty, it opens the visitor's email app.
const FORM_ENDPOINT = "";
// ----------------------------------------------------------------------

document.getElementById("year").textContent = new Date().getFullYear();

// Mobile menu
const btn = document.querySelector(".menu-btn");
const menu = document.getElementById("menu");
btn.addEventListener("click", () => {
  const open = menu.classList.toggle("open");
  btn.setAttribute("aria-expanded", open);
});
menu.addEventListener("click", (e) => {
  if (e.target.tagName === "A") { menu.classList.remove("open"); btn.setAttribute("aria-expanded", false); }
});

// Nav border on scroll
const nav = document.querySelector(".nav");
addEventListener("scroll", () => nav.classList.toggle("scrolled", scrollY > 8), { passive: true });

// Reveal on scroll
const io = "IntersectionObserver" in window && new IntersectionObserver((entries) => {
  entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
}, { threshold: 0.12 });
document.querySelectorAll(".card, .grid-4 > div, .steps li, .work article, .plan").forEach((el) => {
  if (!io) return;
  el.classList.add("reveal");
  io.observe(el);
});

// Plan buttons remember which plan was picked
const form = document.getElementById("lead-form");
document.querySelectorAll("[data-plan]").forEach((a) =>
  a.addEventListener("click", () => { form.plan.value = a.dataset.plan; })
);

// Lead form
const msg = form.querySelector(".form-msg");
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  let ok = true;
  form.querySelectorAll("[required]").forEach((f) => {
    const bad = f.type === "checkbox" ? !f.checked : !f.value.trim() || (f.type === "email" && !/^\S+@\S+\.\S+$/.test(f.value));
    f.classList.toggle("invalid", bad);
    if (bad) ok = false;
  });
  if (!ok) { msg.textContent = "Please fill in every field and tick the box."; return; }

  const d = Object.fromEntries(new FormData(form));
  if (FORM_ENDPOINT) {
    msg.textContent = "Sending…";
    try {
      const r = await fetch(FORM_ENDPOINT, { method: "POST", headers: { Accept: "application/json" }, body: new FormData(form) });
      if (!r.ok) throw new Error(r.status);
      form.reset();
      msg.textContent = "Thanks! We'll be in touch with your free brand review soon.";
    } catch {
      msg.textContent = "Something went wrong. Please email us at " + CONTACT_EMAIL + ".";
    }
    return;
  }
  const body = `Name: ${d.name}\nBusiness: ${d.business}\nEmail: ${d.email}\nPlan: ${d.plan || "-"}\n\nWhat we want to sell more of:\n${d.goal}`;
  location.href = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent("Free brand review: " + d.business)}&body=${encodeURIComponent(body)}`;
  msg.textContent = "Opening your email app to send your request…";
});
