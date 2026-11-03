# Kreova website

A plain static site (HTML, CSS and JS, with no build step). To preview it, open `index.html` in a browser.

## Before going live, replace the placeholders
- `script.js` → `CONTACT_EMAIL` is set to kreova.jm@gmail.com. You can also set `FORM_ENDPOINT` to a Formspree/Basin URL so the form sends without opening the visitor's email app.
- `index.html` → `[INSTAGRAM]` in the footer (email and phone are filled in).
- `[PRICE]` on the Spark and Grow plans.
- Selected work → `[CLIENT NAME]`, `[PROJECT IMAGE]` and results. Only publish results you can back up, and only with the client's permission.

## Deploy (free options)
- **Netlify:** drag the `site/` folder onto app.netlify.com/drop.
- **Cloudflare Pages / Vercel / GitHub Pages:** point it at this repo with `site/` as the output directory.
