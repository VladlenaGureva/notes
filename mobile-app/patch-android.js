// Доводит сгенерированный проект android/: разрешение на точные будильники
// и значок для уведомлений.
const fs = require("fs");
const path = require("path");

const app = path.join(__dirname, "android", "app", "src", "main");
const manifest = path.join(app, "AndroidManifest.xml");
let xml = fs.readFileSync(manifest, "utf8");
const perms = [
  "android.permission.SCHEDULE_EXACT_ALARM",
  "android.permission.POST_NOTIFICATIONS",
  "android.permission.RECEIVE_BOOT_COMPLETED",
];
for (const p of perms) {
  if (!xml.includes(p)) xml = xml.replace("</manifest>", `    <uses-permission android:name="${p}" />\n</manifest>`);
}
fs.writeFileSync(manifest, xml);

const drawable = path.join(app, "res", "drawable");
fs.mkdirSync(drawable, { recursive: true });
fs.copyFileSync(path.join(__dirname, "res", "drawable", "ic_stat_note.xml"), path.join(drawable, "ic_stat_note.xml"));
console.log("android/ доработан");
