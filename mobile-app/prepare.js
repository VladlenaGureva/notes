// Копирует мобильную версию (../docs) в www и кладёт рядом шрифты из ../fonts.
const fs = require("fs");
const path = require("path");

const src = path.join(__dirname, "..", "docs");
const dst = path.join(__dirname, "www");
fs.rmSync(dst, { recursive: true, force: true });
fs.cpSync(src, dst, { recursive: true, filter: (p) => !p.endsWith("sw.js") && !p.endsWith(".nojekyll") });

const fonts = path.join(__dirname, "..", "fonts");
if (fs.existsSync(fonts)) {
  fs.cpSync(fonts, path.join(dst, "fonts"), { recursive: true });
  console.log("шрифты скопированы");
} else {
  console.warn("папка fonts не найдена — будут системные шрифты (запустите tools/fetch_fonts.py)");
}
console.log("готово:", dst);
