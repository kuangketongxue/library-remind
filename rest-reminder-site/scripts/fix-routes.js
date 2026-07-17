/**
 * 修复 Next.js 静态导出的路由问题
 * Cloudflare Pages 需要 contact/index.html 而不是 contact.html
 */
const fs = require('fs');
const path = require('path');

const outDir = path.join(__dirname, '..', 'out');

// 需要修复的页面
const pages = ['contact', 'docs', 'pricing', 'privacy', 'terms', 'rules', 'changelog', 'privacy-chrome'];

for (const page of pages) {
  const htmlFile = path.join(outDir, `${page}.html`);
  const dir = path.join(outDir, page);
  const indexFile = path.join(dir, 'index.html');

  if (fs.existsSync(htmlFile) && fs.existsSync(dir)) {
    fs.copyFileSync(htmlFile, indexFile);
    console.log(`✓ ${page}/index.html`);
  }
}

console.log('Done');
