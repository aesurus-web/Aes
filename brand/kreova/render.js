// Render every SVG in ./svg to PNG at 2x and build preview.png sheet.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch();
  const dir = path.join(__dirname, 'svg'), out = path.join(__dirname, 'png');
  fs.mkdirSync(out, { recursive: true });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const [, w, h] = svg.match(/width="(\d+)" height="(\d+)"/);
    const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 4 });
    await p.setContent(`<style>html,body{margin:0;background:transparent}</style>${svg}`);
    await p.screenshot({ path: path.join(out, f.replace('.svg', '.png')), omitBackground: true });
    await p.close();
  }
  const img = f => `<img src="data:image/svg+xml;base64,${fs.readFileSync(path.join(dir, f)).toString('base64')}">`;
  const card = (label, inner, dark) => `<div class="c${dark ? ' d' : ''}"><span>${label}</span><div class="m">${inner}</div></div>`;
  const p = await b.newPage({ viewport: { width: 1200, height: 1000 }, deviceScaleFactor: 2 });
  await p.setContent(`<style>body{margin:0;padding:48px;font:15px Inter;background:#fff;color:#141414}
  h1{font-size:30px;margin:0 0 28px}.g{display:grid;grid-template-columns:1fr 1fr;gap:20px}
  .c{border:1px solid #e6e6e6;border-radius:16px;padding:20px;height:240px;display:flex;flex-direction:column}
  .c span{color:#555}.d{background:#141414}.d span{color:#aaa}.m{flex:1;display:flex;align-items:center;justify-content:center;gap:24px}
  .m img{max-height:110px;max-width:80%}.m img.i{height:110px}</style>
  <h1>Kreova · Simple directions</h1><div class="g">
  ${card('A · Pure wordmark', img('kreova-a-wordmark.svg'))}
  ${card('B · Wordmark with accent dot', img('kreova-b-wordmark-dot.svg'))}
  ${card('C · Circle mark + wordmark', img('kreova-c-lockup.svg'))}
  ${card('D · Icon only (social / app)', img('kreova-d-icon-dark.svg').replace('<img','<img class="i"') + img('kreova-d-icon-light.svg').replace('<img','<img class="i"'))}
  ${card('B · Reversed', img('kreova-b-wordmark-dot-white.svg'), 1)}
  ${card('C · Reversed', img('kreova-c-lockup-white.svg'), 1)}
  </div>`);
  await p.screenshot({ path: path.join(__dirname, 'preview.png'), fullPage: true });
  await b.close();
})();
