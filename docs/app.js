/* Заметки — мобильная версия (PWA). Формат данных совпадает с версией для Windows,
   поэтому файл .stickies_data.json можно переносить между ними. */
"use strict";

// В приложении для Android (Capacitor) доступны системные возможности
const CAP = window.Capacitor;
const NATIVE = !!(CAP && CAP.isNativePlatform && CAP.isNativePlatform());
const PL = NATIVE ? CAP.Plugins : {};

// ============================ язык ============================
const STR = {
  app: ["Заметки", "Notes"],
  search: ["Поиск", "Search"],
  archive: ["Архив", "Done"],
  settings: ["Настройки", "Settings"],
  today: ["Сегодня", "Today"],
  tomorrow: ["Завтра", "Tomorrow"],
  yesterday: ["Вчера", "Yesterday"],
  mark_today: ["СЕГОДНЯ", "TODAY"],
  mark_tomorrow: ["ЗАВТРА", "TOMORROW"],
  mark_yesterday: ["ВЧЕРА", "YESTERDAY"],
  new_note: ["Новая заметка", "New note"],
  no_notes: ["Заметок нет", "No notes"],
  n_done: ["{n} выполнено", "{n} done"],
  empty_quote: ["Красота — в мелочах", "There is beauty in small things"],
  empty_hint_m: ["Нажмите «+», чтобы добавить заметку", "Tap “+” to add a note"],
  placeholder: ["Заметка…", "Note…"],
  tag_yandex: ["ЯНДЕКС", "YANDEX"],
  tag_plan: ["ОБЯЗАТЕЛЬНО", "DAILY"],
  plan_text: ["Заполнить заметки на завтра", "Fill in tomorrow's notes"],
  carry: ["Незавершённое из прошлых дней: <b>{n}</b>. Перенести на сегодня", "Unfinished from past days: <b>{n}</b>. Move to today"],
  carried: ["Перенесено на сегодня: {n}", "Moved to today: {n}"],
  done_toast: ["Выполнено", "Done"],
  deleted_toast: ["Удалено", "Deleted"],
  moved_toast: ["Перенесено: {d}", "Moved to {d}"],
  undo: ["Отменить", "Undo"],
  m_color: ["Цвет", "Colour"],
  m_reminder: ["Напоминание", "Reminder"],
  m_repeat: ["Повторять", "Repeat"],
  m_move_to: ["Перенести на другой день", "Move to another day"],
  m_move_today: ["Перенести на сегодня", "Move to today"],
  m_duplicate: ["Дублировать", "Duplicate"],
  m_open_tomorrow: ["Открыть завтрашний день", "Open tomorrow"],
  m_delete: ["Удалить", "Delete"],
  btn_done: ["Выполнено", "Done"],
  btn_more: ["Ещё", "More"],
  move_title: ["Перенести заметку", "Move note"],
  move_btn: ["Перенести", "Move"],
  cancel: ["Отмена", "Cancel"],
  save: ["Сохранить", "Save"],
  q_day_after: ["Послезавтра", "Day after"],
  q_monday: ["Понедельник", "Monday"],
  q_week: ["Через неделю", "In a week"],
  rem_title: ["Напоминание", "Reminder"],
  rem_twice: ["Дважды в день", "Twice a day"],
  rem_once: ["Один раз", "Once"],
  rem_off: ["Без напоминания", "No reminder"],
  rem_hint_twice: ["Уведомление появится дважды в день, пока заметка не выполнена.", "You'll get a notification twice a day until the note is done."],
  rem_hint_after12: ["Заметка создана после 12:00 — сегодня одно напоминание.", "The note was created after 12:00, so one reminder today."],
  rem_hint_mobile: ["На телефоне напоминания надёжно приходят, пока приложение открыто или свёрнуто недавно.", "On phones, reminders arrive reliably while the app is open or recently backgrounded."],
  rep_title: ["Повторять заметку", "Repeat note"],
  rep_none: ["Не повторять", "Don't repeat"],
  rep_daily: ["Каждый день", "Every day"],
  rep_weekdays: ["По будням", "On weekdays"],
  rep_days: ["По дням недели", "On these days"],
  rep_monthly: ["Каждый месяц, {n} числа", "Every month on the {n}"],
  rep_hint: ["Заметка будет сама появляться в выбранные дни. Начало повтора: {d}.", "The note will appear on the chosen days, starting {d}."],
  rep_txt_daily: ["каждый день", "every day"],
  rep_txt_weekdays: ["по будням", "weekdays"],
  rep_txt_monthly: ["{n} числа", "monthly, {n}"],
  popup_title: ["Напоминание", "Reminder"],
  popup_done: ["Готово", "Done"],
  popup_snooze: ["Через {n} мин", "In {n} min"],
  popup_open: ["Открыть", "Open"],
  popup_close: ["Закрыть", "Close"],
  calendar: ["Календарь", "Calendar"],
  done_title: ["Выполнено", "Completed"],
  archive_empty: ["Выполненные заметки этого дня появятся здесь.", "Completed notes for this day will appear here."],
  restore: ["Вернуть", "Restore"],
  delete: ["Удалить", "Delete"],
  search_ph: ["Поиск по всем заметкам", "Search all notes"],
  nothing_found: ["Ничего не найдено", "Nothing found"],
  archive_suffix: [" · архив", " · done"],
  set_look: ["Внешний вид", "Appearance"],
  set_lang: ["Язык", "Language"],
  set_theme: ["Тема", "Theme"],
  theme_auto: ["Как в системе", "System"],
  theme_light: ["Светлая", "Light"],
  theme_dark: ["Тёмная", "Dark"],
  set_palette: ["Палитра стикеров", "Sticker palette"],
  set_font: ["Шрифт стикеров", "Sticker font"],
  set_size: ["Размер шрифта", "Font size"],
  set_flowers: ["Сухоцвет на доске", "Dried flowers on the board"],
  set_reminders: ["Напоминания", "Reminders"],
  set_morning: ["Утреннее", "Morning"],
  set_evening: ["Вечернее", "Evening"],
  set_plan: ["Обязательная заметка", "Daily required note"],
  set_plan_hint: ["Каждый будний день и в воскресенье появляется заметка «Заполнить заметки на завтра».", "Every weekday and on Sunday the note “Fill in tomorrow's notes” appears."],
  set_notify: ["Разрешить уведомления", "Allow notifications"],
  notify_on: ["Уведомления разрешены", "Notifications allowed"],
  notify_denied: ["Уведомления запрещены в настройках браузера", "Notifications are blocked in browser settings"],
  set_data: ["Данные", "Data"],
  export: ["Сохранить копию заметок (.json)", "Export notes (.json)"],
  import: ["Загрузить заметки из файла", "Import notes from a file"],
  data_hint: ["Файл совместим с версией для Windows (.stickies_data.json в папке пользователя). При загрузке заметки добавляются к имеющимся.", "The file is compatible with the Windows version (.stickies_data.json in your user folder). Imported notes are added to existing ones."],
  imported: ["Добавлено заметок: {n}", "Notes added: {n}"],
  import_fail: ["Не удалось прочитать файл", "Could not read the file"],
  install_hint: ["Чтобы поставить на главный экран: меню браузера → «Добавить на главный экран».", "To install: browser menu → “Add to Home screen”."],
  rem_hint_native: ["Напоминание придёт системным уведомлением, даже если приложение закрыто.", "The reminder arrives as a system notification even when the app is closed."],
  exported: ["Копия сохранена", "Backup saved"],
  empty: ["(пусто)", "(empty)"],
};
const MONTHS_GEN = {
  ru: ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"],
  en: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
};
const MONTHS_NOM = { ru: ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"], en: MONTHS_GEN.en };
const WEEKDAYS = { ru: ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"], en: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] };
const WD_SHORT = { ru: ["пн", "вт", "ср", "чт", "пт", "сб", "вс"], en: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] };

let LANG = "ru";
function T(key, kw) {
  const pair = STR[key];
  if (!pair) return key;
  let s = LANG === "ru" ? pair[0] : pair[1];
  if (kw) for (const k in kw) s = s.split("{" + k + "}").join(kw[k]);
  return s;
}
function pluralRu(n, a, b, c) {
  n = Math.abs(n);
  if (n % 10 === 1 && n % 100 !== 11) return a;
  if (n % 10 >= 2 && n % 10 <= 4 && !(n % 100 >= 12 && n % 100 <= 14)) return b;
  return c;
}
function countText(n) {
  return LANG === "ru" ? `${n} ${pluralRu(n, "заметка", "заметки", "заметок")}` : `${n} ${n === 1 ? "note" : "notes"}`;
}

// ============================ даты ============================
const pad = (n) => String(n).padStart(2, "0");
const keyOf = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const parseKey = (k) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(k || ""); return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null; };
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const wd = (d) => (d.getDay() + 6) % 7; // пн = 0
const todayKey = () => keyOf(new Date());
const nowIso = () => { const d = new Date(); return `${keyOf(d)}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`; };
const parseIso = (s) => { if (!s) return null; const d = new Date(String(s)); return isNaN(d) ? null : d; };
const parseHM = (s) => { const m = /^(\d{1,2}):(\d{1,2})/.exec(String(s || "")); if (!m) return null; const h = +m[1], mi = +m[2]; return h < 24 && mi < 60 ? [h, mi] : null; };
const fmtHM = (h, m) => `${pad(h)}:${pad(m)}`;
function dayMonth(d, withYear) {
  if (LANG === "ru") return `${d.getDate()} ${MONTHS_GEN.ru[d.getMonth()]}${withYear ? " " + d.getFullYear() : ""}`;
  return `${MONTHS_GEN.en[d.getMonth()]} ${d.getDate()}${withYear ? ", " + d.getFullYear() : ""}`;
}
function humanDate(d, today) {
  today = today || parseKey(todayKey());
  const delta = Math.round((d - today) / 864e5);
  if (delta === 0) return T("today");
  if (delta === 1) return T("tomorrow");
  if (delta === -1) return T("yesterday");
  if (d.getFullYear() !== today.getFullYear()) return dayMonth(d, true);
  return `${dayMonth(d)}, ${WD_SHORT[LANG][wd(d)]}`;
}
const inline = (s) => (LANG === "ru" ? s.charAt(0).toLowerCase() + s.slice(1) : s);

// ============================ палитры ============================
const PALETTES = {
  kraft: { name: ["Крафт и бумага", "Kraft & paper"], colors: ["#F2EADA", "#DCC39C", "#D5DBD6", "#D4D8BE", "#EAD3C6", "#DDD4D8", "#EFE7D4"], grid: 6,
    names: [["Сливки", "Крафт", "Туман", "Шалфей", "Пудра", "Вереск", "Клетка"], ["Cream", "Kraft", "Mist", "Sage", "Powder", "Heather", "Grid"]] },
  pastel: { name: ["Пастель", "Pastel"], colors: ["#F6E7A1", "#F4CFA8", "#C5DBF0", "#CFE5C6", "#EFC9D3", "#D9D0EC", "#F3EAD3"],
    names: [["Лимон", "Персик", "Небо", "Мята", "Роза", "Лаванда", "Крем"], ["Lemon", "Peach", "Sky", "Mint", "Rose", "Lavender", "Cream"]] },
  nature: { name: ["Природа", "Nature"], colors: ["#EADDB4", "#E3B99C", "#CAD7D8", "#C5D0AB", "#E7C5B7", "#D0C7D6", "#E9E4D4"],
    names: [["Пшеница", "Терракота", "Иней", "Мох", "Глина", "Чабрец", "Лён"], ["Wheat", "Terracotta", "Frost", "Moss", "Clay", "Thyme", "Linen"]] },
  classic: { name: ["Классика", "Classic"], colors: ["#FFF27A", "#FFC58A", "#A9D8F5", "#B7E4A8", "#F9B4C0", "#D3C0F0", "#FFFDF5"],
    names: [["Жёлтый", "Оранжевый", "Голубой", "Зелёный", "Розовый", "Сиреневый", "Белый"], ["Yellow", "Orange", "Blue", "Green", "Pink", "Lilac", "White"]] },
};
const LEGACY = { "#FFF9A6": 0, "#FFD6A5": 1, "#BDE0FE": 2, "#C8F7C5": 3, "#F8C8DC": 4, "#E0D3F5": 5, "#FFF1B8": 6 };
const FONTS = [
  ["Caveat", '"Caveat", cursive', 21], ["Marck Script", '"Marck Script", cursive', 19],
  ["Lora", '"Lora", Georgia, serif', 16], ["PT Serif", '"PT Serif", Georgia, serif', 16],
  ["PT Sans", '"PT Sans", system-ui, sans-serif', 16], ["System", "system-ui, sans-serif", 16],
];
function colorIndex(hex) {
  if (typeof hex !== "string") return 0;
  const up = hex.toUpperCase();
  if (up in LEGACY) return LEGACY[up];
  for (const p of Object.values(PALETTES)) { const i = p.colors.findIndex((c) => c.toUpperCase() === up); if (i >= 0) return i; }
  return 0;
}
const palette = () => PALETTES[cfg.palette] || PALETTES.kraft;
const noteColor = (ci) => palette().colors[(ci || 0) % 7];

// ============================ хранилище ============================
const DATA_KEY = "notes.data.v1", CFG_KEY = "notes.config.v1";
const DEFAULT_CFG = { lang: (navigator.language || "ru").startsWith("ru") ? "ru" : "en", theme: "auto", palette: "kraft",
  font: "Caveat", size: 21, flowers: true, remind_morning: "10:00", remind_evening: "17:00", plan_time: "20:00", plan_days: [] };
let cfg = { ...DEFAULT_CFG };
let days = {};        // { "2026-10-22": { active: [...], archived: [...] } }
let recurring = [];   // шаблоны повторов

function uid() { return (crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2)); }
function normalizeNote(n) {
  if (!n || typeof n !== "object") return null;
  const out = { ...n };
  out.id = String(out.id || uid());
  out.text = typeof out.text === "string" ? out.text : out.text == null ? "" : String(out.text);
  if (!Number.isInteger(out.ci) || out.ci < 0 || out.ci > 6) out.ci = colorIndex(out.color);
  if (out.remind) {
    const times = (out.remind.times || []).map(parseHM).filter(Boolean).map((t) => fmtHM(t[0], t[1]));
    if (times.length) out.remind = { ...out.remind, times: [...new Set(times)].sort() }; else delete out.remind;
  }
  if (!Array.isArray(out.fired)) delete out.fired;
  return out;
}
function normalizeData(raw) {
  const res = { days: {}, recurring: [] };
  if (!raw || typeof raw !== "object") return res;
  if (Array.isArray(raw)) raw = { [todayKey()]: { active: raw, archived: [] } };
  if (Array.isArray(raw.active)) raw = { [todayKey()]: { active: raw.active, archived: raw.archived || [] } };
  for (const [k, v] of Object.entries(raw)) {
    if (k === "_recurring") { if (Array.isArray(v)) res.recurring = v.filter((t) => t && t.id && normRule(t.rule)).map((t) => ({ ...t, rule: normRule(t.rule), skip: t.skip || [] })); continue; }
    if (!v || typeof v !== "object") continue;
    res.days[k] = { active: (v.active || []).map(normalizeNote).filter(Boolean), archived: (v.archived || []).map(normalizeNote).filter(Boolean) };
  }
  return res;
}
function serialize() {
  const out = {};
  for (const [k, v] of Object.entries(days)) if (v.active.length || v.archived.length) out[k] = v;
  if (recurring.length) out._recurring = recurring;
  return out;
}
function load() {
  try { cfg = { ...DEFAULT_CFG, ...(JSON.parse(localStorage.getItem(CFG_KEY) || "{}")) }; } catch (e) { cfg = { ...DEFAULT_CFG }; }
  try { const d = normalizeData(JSON.parse(localStorage.getItem(DATA_KEY) || "{}")); days = d.days; recurring = d.recurring; } catch (e) { days = {}; recurring = []; }
}
let saveTimer = null;
function save(now) {
  clearTimeout(saveTimer);
  const doit = () => { try { localStorage.setItem(DATA_KEY, JSON.stringify(serialize())); } catch (e) { console.warn(e); } scheduleNative(); };
  if (now) doit(); else saveTimer = setTimeout(doit, 300);
}
function saveCfg() { try { localStorage.setItem(CFG_KEY, JSON.stringify(cfg)); } catch (e) { console.warn(e); } }
const day = (k) => (days[k] || (days[k] = { active: [], archived: [] }));
const peek = (k) => days[k] || { active: [], archived: [] };

// ============================ напоминания и повторы ============================
function defaultReminder(noteDay, created, now) {
  created = created || now;
  const ev = parseHM(cfg.remind_evening) || [17, 0], mo = parseHM(cfg.remind_morning) || [10, 0];
  if (keyOf(created) === keyOf(noteDay) && created.getHours() >= 12) {
    const evDt = new Date(noteDay); evDt.setHours(ev[0], ev[1], 0, 0);
    if (keyOf(noteDay) === keyOf(now) && evDt <= now) {
      let soon = new Date(now.getTime() + 3600e3); soon.setMinutes(Math.floor(soon.getMinutes() / 5) * 5, 0, 0);
      if (keyOf(soon) !== keyOf(now)) { soon = new Date(now); soon.setHours(23, 55, 0, 0); }
      return ["once", [fmtHM(soon.getHours(), soon.getMinutes())]];
    }
    return ["once", [fmtHM(ev[0], ev[1])]];
  }
  return ["twice", [...new Set([fmtHM(mo[0], mo[1]), fmtHM(ev[0], ev[1])])].sort()];
}
function dueReminders(note, dk, now) {
  const r = note.remind;
  if (!r || dk !== keyOf(now)) return [[], false];
  const since = parseIso(r.since) || new Date(0);
  const fired = new Set(note.fired || []);
  const due = [];
  for (const t of [...new Set(r.times || [])].sort()) {
    const hm = parseHM(t); if (!hm) continue;
    const at = new Date(now); at.setHours(hm[0], hm[1], 0, 0);
    const k = `${dk} ${fmtHM(hm[0], hm[1])}`;
    if (at > since && at <= now && now - at <= 12 * 3600e3 && !fired.has(k)) due.push(k);
  }
  const sn = parseIso(r.snooze);
  return [due, !!(sn && sn <= now)];
}
function normRule(r) {
  if (!r || typeof r !== "object") return null;
  if (r.kind === "daily" || r.kind === "weekdays") return { kind: r.kind };
  if (r.kind === "days") { const d = [...new Set((r.days || []).map(Number).filter((x) => x >= 0 && x <= 6))].sort(); return d.length ? { kind: "days", days: d } : null; }
  if (r.kind === "monthly") { const dom = parseInt(r.dom, 10); return dom >= 1 && dom <= 31 ? { kind: "monthly", dom } : null; }
  return null;
}
function ruleMatches(r, d) {
  r = normRule(r); if (!r) return false;
  if (r.kind === "daily") return true;
  if (r.kind === "weekdays") return wd(d) < 5;
  if (r.kind === "days") return r.days.includes(wd(d));
  const last = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
  return d.getDate() === Math.min(r.dom, last);
}
function ruleText(r) {
  r = normRule(r); if (!r) return "";
  if (r.kind === "daily") return T("rep_txt_daily");
  if (r.kind === "weekdays") return T("rep_txt_weekdays");
  if (r.kind === "days") {
    if (r.days.join() === "0,1,2,3,4") return T("rep_txt_weekdays");
    if (r.days.length === 7) return T("rep_txt_daily");
    return r.days.map((x) => WD_SHORT[LANG][x]).join(", ");
  }
  return T("rep_txt_monthly", { n: r.dom });
}
const template = (rid) => recurring.find((t) => t.id === rid);
function setRule(note, dk, rule) {
  rule = normRule(rule); if (!rule) return null;
  let t = note.rid ? template(note.rid) : null;
  if (!t) { t = { id: "r-" + uid(), start: dk, skip: [] }; recurring.push(t); }
  else { t.start = t.start < dk ? t.start : dk; t.skip = (t.skip || []).filter((k) => k !== dk); }
  Object.assign(t, { text: note.text, ci: note.ci, w: note.w || 240, h: note.h || 206, rule, times: note.remind ? [...note.remind.times] : [] });
  return t.id;
}
function skip(rid, dk) { const t = template(rid); if (t && !t.skip.includes(dk)) t.skip.push(dk); }
function materialize(dk) {
  const d = parseKey(dk); if (!d || dk < todayKey()) return 0;
  const b = day(dk);
  const have = new Set([...b.active, ...b.archived].map((n) => n.rid).filter(Boolean));
  let added = 0;
  for (const t of recurring) {
    if (have.has(t.id) || dk < t.start || (t.skip || []).includes(dk) || !ruleMatches(t.rule, d)) continue;
    const n = { id: uid(), rid: t.id, text: t.text || "", ci: t.ci || 0, w: t.w || 240, h: t.h || 206, x: 28, y: 28, created: `${dk}T00:00:00` };
    if (t.times && t.times.length) n.remind = { mode: t.times.length > 1 ? "twice" : "once", times: [...t.times], since: `${dk}T00:00:00` };
    b.active.push(n); added++;
  }
  return added;
}
function ensurePlan() {
  const tk = todayKey(), d = parseKey(tk);
  if (wd(d) === 5 || (cfg.plan_days || []).includes(tk)) return false;
  const b = peek(tk);
  if ([...b.active, ...b.archived].some((n) => n.kind === "plan")) return false;
  day(tk).active.push({ id: uid(), text: T("plan_text"), ci: 0, kind: "plan", w: 240, h: 206, x: 28, y: 28, created: nowIso(),
    remind: { mode: "once", times: [cfg.plan_time || "20:00"], since: `${tk}T00:00:00` } });
  cfg.plan_days = [...(cfg.plan_days || []), tk].slice(-40);
  saveCfg(); save(true);
  return true;
}
function overdueKeys() { const tk = todayKey(); return Object.keys(days).filter((k) => parseKey(k) && k < tk && days[k].active.length).sort(); }
function carryOverdue() {
  const tk = todayKey(), td = parseKey(tk); let moved = 0;
  for (const k of overdueKeys()) {
    const list = days[k].active; days[k].active = [];
    for (const n of list) {
      if (n.kind === "plan") { n.done_at = nowIso(); days[k].archived.push(n); continue; }
      const t = n.rid ? template(n.rid) : null;
      if (t && ruleMatches(t.rule, td) && tk >= t.start) continue;
      delete n.rid; delete n.fired; day(tk).active.push(n); moved++;
    }
  }
  save(true); return moved;
}

// ============================ текстуры и рваные края ============================
function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function hash(str) { let h = 2166136261; for (const c of String(str)) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; }
function texture(base, density, dark, light, fibers, seed) {
  const S = 220, cv = document.createElement("canvas"); cv.width = cv.height = S;
  const g = cv.getContext("2d"), r = rng(seed);
  if (base) { g.fillStyle = base; g.fillRect(0, 0, S, S); }
  for (let i = 0; i < S * S * density; i++) {
    const dk = r() < 0.55;
    g.fillStyle = dk ? `rgba(${dark},${(8 + r() * 18) / 255})` : `rgba(${light},${(10 + r() * 24) / 255})`;
    g.fillRect(Math.floor(r() * S), Math.floor(r() * S), 1, 1);
  }
  g.lineWidth = 0.7;
  for (let i = 0; i < fibers; i++) {
    const x = r() * S, y = r() * S, a = r() * Math.PI, l = 3 + r() * 8;
    g.strokeStyle = `rgba(${dark},${(14 + r() * 26) / 255})`;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + l * Math.cos(a), y + l * Math.sin(a)); g.stroke();
  }
  for (let i = 0; i < S * S / 5200; i++) { g.fillStyle = `rgba(${dark},${(50 + r() * 60) / 255})`; g.beginPath(); g.arc(r() * S, r() * S, 0.5 + r() * 0.6, 0, 7); g.fill(); }
  return `url(${cv.toDataURL()})`;
}
function applyTextures() {
  const st = document.documentElement.style, dark = document.documentElement.dataset.theme === "dark";
  const cs = getComputedStyle(document.documentElement);
  st.setProperty("--kraft-tex", dark ? texture(cs.getPropertyValue("--kraft").trim(), 0.2, "0,0,0", "120,100,80", 90, 11)
    : texture(cs.getPropertyValue("--kraft").trim(), 0.26, "70,50,30", "225,205,175", 140, 7));
  st.setProperty("--paper-tex", dark ? texture(cs.getPropertyValue("--paper").trim(), 0.1, "0,0,0", "90,80,70", 40, 13)
    : texture(cs.getPropertyValue("--paper").trim(), 0.12, "110,85,60", "255,255,250", 60, 5));
  if (!applyTextures.speck) applyTextures.speck = texture(null, 0.1, "90,65,40", "255,255,248", 50, 3);
  st.setProperty("--speckle", applyTextures.speck);
}
function tornPolygon(w, h, seed, amp = 2.4, step = 5, sides = "tlbr") {
  const r = rng(seed), pts = [];
  const edge = (x0, y0, x1, y1, nx, ny, on) => {
    if (!on) { pts.push([x0, y0]); return; }
    const len = Math.hypot(x1 - x0, y1 - y0), n = Math.max(2, Math.floor(len / step)), ph = r() * 6.28, fq = (0.6 + r() * 0.8) * len / 60;
    for (let i = 0; i < n; i++) {
      const t = i / n; let off = -amp * (0.5 + 0.5 * Math.sin(ph + t * fq * 6.28)) * 0.7 - r() * amp;
      if (r() < 0.035) off -= amp * (0.8 + r() * 0.8);
      pts.push([x0 + (x1 - x0) * t - nx * off * -1, y0 + (y1 - y0) * t - ny * off * -1]);
    }
  };
  edge(0, 0, w, 0, 0, -1, sides.includes("t"));
  edge(w, 0, w, h, 1, 0, sides.includes("r"));
  edge(w, h, 0, h, 0, 1, sides.includes("b"));
  edge(0, h, 0, 0, -1, 0, sides.includes("l"));
  return `polygon(${pts.map(([x, y]) => `${x.toFixed(1)}px ${y.toFixed(1)}px`).join(",")})`;
}
const clipObserver = new ResizeObserver((entries) => {
  for (const e of entries) {
    const el = e.target, w = el.offsetWidth, h = el.offsetHeight;
    if (!w || !h) continue;
    if (el.dataset.cw == w && el.dataset.ch == h) continue;
    el.dataset.cw = w; el.dataset.ch = h;
    if (el.classList.contains("paper-head")) el.style.setProperty("--head-clip", tornPolygon(w, h + 1, 202, 3, 4, "b"));
    else el.style.setProperty("--clip", tornPolygon(w, h, +el.dataset.seed || 1, +el.dataset.amp || 2.4));
  }
});
function tear(el, seed, amp) { el.dataset.seed = seed; if (amp) el.dataset.amp = amp; clipObserver.observe(el); }

function flowersSVG() {
  const W = 280, H = 340, r = rng(42), base = [W - 78, H - 26], stems = [], clusters = [];
  const qp = (a, b, c, t) => (1 - t) * (1 - t) * a + 2 * (1 - t) * t * b + t * t * c;
  for (let i = 0; i < 5; i++) {
    const ang = (-34 + i * 9 + (r() * 8 - 4)) * Math.PI / 180, len = 200 + r() * 60 - Math.abs(i - 2) * 12, bend = r() * 36 - 18;
    const s = [base[0] + r() * 10 - 5, base[1] + r() * 8 - 4], e = [s[0] + Math.sin(ang) * len, s[1] - Math.cos(ang) * len];
    const c = [(s[0] + e[0]) / 2 + bend, (s[1] + e[1]) / 2];
    stems.push(`<path d="M${s} Q${c} ${e}" stroke-width="1.4"/>`); clusters.push(e);
    const nb = 2 + Math.floor(r() * 3);
    for (let j = 0; j < nb; j++) {
      const t = 0.45 + r() * 0.45, p = [qp(s[0], c[0], e[0], t), qp(s[1], c[1], e[1], t)];
      const a2 = ang + (r() < 0.5 ? -1 : 1) * (18 + r() * 20) * Math.PI / 180, l = 26 + r() * 32;
      const tip = [p[0] + Math.sin(a2) * l, p[1] - Math.cos(a2) * l];
      stems.push(`<path d="M${p} L${tip}" stroke-width="0.9"/>`); clusters.push(tip);
    }
  }
  let twigs = "", shadows = "", petals = "";
  for (const c of clusters) {
    const n = 6 + Math.floor(r() * 6);
    for (let i = 0; i < n; i++) {
      const a = r() * 6.28, rr = 3 + r() * 12, f = [c[0] + Math.cos(a) * rr, c[1] + Math.sin(a) * rr * 0.8 - 3], sz = 2.1 + r() * 0.9, rot = r() * 6.28, tone = r();
      twigs += `<line x1="${c[0].toFixed(1)}" y1="${c[1].toFixed(1)}" x2="${f[0].toFixed(1)}" y2="${f[1].toFixed(1)}"/>`;
      shadows += `<circle cx="${(f[0] + 3).toFixed(1)}" cy="${(f[1] + 5).toFixed(1)}" r="${(sz * 1.9).toFixed(1)}"/>`;
      const fill = `rgb(${Math.round(240 - 22 * tone)},${Math.round(228 - 32 * tone)},${Math.round(206 - 48 * tone)})`;
      for (let k = 0; k < 5; k++) { const aa = rot + k * 1.2566; petals += `<circle cx="${(f[0] + Math.cos(aa) * sz * 0.85).toFixed(1)}" cy="${(f[1] + Math.sin(aa) * sz * 0.85).toFixed(1)}" r="${(sz * 0.72).toFixed(1)}" fill="${fill}"/>`; }
      petals += `<circle cx="${f[0].toFixed(1)}" cy="${f[1].toFixed(1)}" r="${(sz * 0.38).toFixed(1)}" fill="#9A7448" stroke="none"/>`;
    }
  }
  const st = stems.join("");
  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="rgba(40,25,10,.15)" transform="translate(3 5)">${st}</g>
    <g fill="rgba(40,25,10,.12)">${shadows}</g>
    <g fill="none" stroke="#8C7150" stroke-linecap="round">${st}</g>
    <g stroke="#8C7150" stroke-width="0.6">${twigs}</g>
    <g stroke="rgba(150,120,80,.45)" stroke-width="0.5">${petals}</g>
    <g transform="translate(${base[0] - 8} ${base[1] - 42}) rotate(-12)"><polygon points="-39,-11.5 39,-11.5 37,-4 39,4 37,11.5 -39,11.5 -37,4 -39,-4" fill="rgba(238,229,209,.82)"/></g>
  </svg>`;
}

// ============================ интерфейс ============================
const $ = (s) => document.querySelector(s);
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const ICON = {
  check: '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  more: '<svg viewBox="0 0 24 24"><circle cx="6" cy="12" r="1.3" fill="currentColor"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/><circle cx="18" cy="12" r="1.3" fill="currentColor"/></svg>',
  bell: '<svg viewBox="0 0 24 24"><path d="M6 16.5l1-1.6V10a5 5 0 0110 0v4.9l1 1.6z"/><circle cx="12" cy="19" r="1.6"/></svg>',
  repeat: '<svg viewBox="0 0 24 24"><path d="M19 12a7 7 0 11-2.1-5" /><path d="M17.5 3.5v4h-4"/></svg>',
  move: '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 9.5h16M9 3v4M15 3v4"/></svg>',
  copy: '<svg viewBox="0 0 24 24"><rect x="8" y="8" width="11" height="11" rx="2"/><path d="M5 15V6a1 1 0 011-1h9"/></svg>',
  trash: '<svg viewBox="0 0 24 24"><path d="M5 7h14M10 7V5h4v2M7 7l1 12h8l1-12"/></svg>',
  today: '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12l7 7 7-7"/></svg>',
  clip: '<svg viewBox="0 0 16 42"><path d="M10.5 10v24a4.6 4.6 0 01-9.2 0V7.5a6.4 6.4 0 0112.8 0V30"/></svg>',
};

let current = todayKey();
let weekStart = null;
const undoStack = [];

function applyTheme() {
  const t = cfg.theme === "auto" ? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : cfg.theme;
  document.documentElement.dataset.theme = t;
  const f = FONTS.find((x) => x[0] === cfg.font) || FONTS[0];
  document.documentElement.style.setProperty("--note-font", f[1]);
  document.documentElement.style.setProperty("--note-size", (cfg.size || f[2]) + "px");
  document.documentElement.lang = LANG;
  document.title = T("app");
  $("#flowers").hidden = !cfg.flowers;
  applyTextures();
}
function translateStatic() {
  document.querySelectorAll("[data-t]").forEach((e) => (e.textContent = T(e.dataset.t)));
  document.querySelectorAll("[data-t-aria]").forEach((e) => e.setAttribute("aria-label", T(e.dataset.tAria)));
}

function renderHeader() {
  const d = parseKey(current), td = parseKey(todayKey());
  const delta = Math.round((d - td) / 864e5);
  const mark = { 0: T("mark_today"), 1: T("mark_tomorrow"), "-1": T("mark_yesterday") }[delta];
  $("#weekday").textContent = WEEKDAYS[LANG][wd(d)].toUpperCase() + (mark ? "  ·  " + mark : "");
  $("#date-title").textContent = dayMonth(d, d.getFullYear() !== td.getFullYear());
  const b = peek(current), parts = [];
  if (b.active.length) parts.push(countText(b.active.length));
  if (b.archived.length) parts.push(T("n_done", { n: b.archived.length }));
  $("#stats").textContent = parts.length ? parts.join("  ·  ") : T("no_notes");
  $("#btn-today").disabled = delta === 0;
  const badge = $("#archive-count"); badge.hidden = !b.archived.length; badge.textContent = b.archived.length;
  if (!weekStart || d < weekStart || d >= addDays(weekStart, 7)) weekStart = addDays(d, -wd(d));
  const wrap = $("#week-days"); wrap.innerHTML = "";
  for (let i = 0; i < 7; i++) {
    const x = addDays(weekStart, i), k = keyOf(x);
    const btn = el("button", "day" + (k === current ? " sel" : "") + (k === todayKey() ? " today" : "") + (peek(k).active.length ? " has" : ""),
      `<span class="dn">${WD_SHORT[LANG][i]}</span><span class="dd">${x.getDate()}</span><span class="dot"></span>`);
    btn.onclick = () => showDay(k);
    wrap.appendChild(btn);
  }
  const od = overdueKeys().reduce((s, k) => s + days[k].active.length, 0);
  const banner = $("#carry"); banner.hidden = !od; banner.innerHTML = T("carry", { n: od });
}

function noteCard(n) {
  const wrap = el("div", "note-wrap");
  const seed = hash(n.id);
  const card = el("div", "note" + (palette().grid === n.ci ? " grid" : ""));
  card.style.setProperty("--c", noteColor(n.ci));
  const deco = n.kind === "plan" ? 2 : seed % 3;
  if (deco === 2) { const c = el("div", "clip", ICON.clip); wrap.appendChild(c); }
  else { const t = el("div", "tape"); t.style.left = deco === 0 ? "36%" : "12px"; t.style.transform = `rotate(${deco === 0 ? (seed % 7) - 3 : -9}deg)`; wrap.appendChild(t); }
  const top = el("div", "note-top");
  if (deco === 2) top.appendChild(el("span", "", "&nbsp;&nbsp;&nbsp;&nbsp;"));
  if (n.kind === "plan") top.appendChild(el("span", "tag plan", T("tag_plan")));
  else if (n.source === "yandex") top.appendChild(el("span", "tag", T("tag_yandex")));
  card.appendChild(top);
  const ta = el("textarea"); ta.value = n.text; ta.placeholder = T("placeholder"); ta.rows = 2;
  const grow = () => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + "px"; };
  ta.addEventListener("input", () => { n.text = ta.value; grow(); save(); });
  card.appendChild(ta);
  const bottom = el("div", "note-bottom");
  if (n.remind && n.remind.times && n.remind.times.length) {
    const parts = [...n.remind.times]; const sn = parseIso(n.remind.snooze); if (sn) parts.push(fmtHM(sn.getHours(), sn.getMinutes()));
    const m = el("button", "meta bell", ICON.bell + esc(parts.join(" · "))); m.onclick = () => reminderSheet(n); bottom.appendChild(m);
  }
  const t = n.rid ? template(n.rid) : null;
  if (t) { const m = el("button", "meta", ICON.repeat + esc(ruleText(t.rule))); m.onclick = () => repeatSheet(n); bottom.appendChild(m); }
  const acts = el("div", "note-actions");
  const done = el("button", "", ICON.check); done.setAttribute("aria-label", T("btn_done")); done.onclick = () => completeNote(n);
  const more = el("button", "", ICON.more); more.setAttribute("aria-label", T("btn_more")); more.onclick = () => noteMenu(n);
  acts.append(done, more); bottom.appendChild(acts); card.appendChild(bottom);
  wrap.appendChild(card);
  tear(card, seed);
  requestAnimationFrame(grow);
  wrap.dataset.id = n.id;
  return wrap;
}
function renderBoard() {
  const list = $("#notes"); list.innerHTML = "";
  const b = peek(current);
  b.active.forEach((n) => list.appendChild(noteCard(n)));
  $("#empty").hidden = b.active.length > 0;
}
function render() { renderHeader(); renderBoard(); }

function showDay(k) {
  if (materialize(k)) save(true);
  current = k; render(); window.scrollTo({ top: 0 });
}
function focusNote(id) {
  const w = document.querySelector(`.note-wrap[data-id="${CSS.escape(id)}"]`);
  if (w) { w.scrollIntoView({ block: "center", behavior: "smooth" }); const ta = w.querySelector("textarea"); setTimeout(() => ta && ta.focus(), 250); }
}

// ---------- действия ----------
function toast(text, undo) {
  const tb = $("#toast"); $("#toast-text").textContent = text;
  const btn = $("#toast-btn"); btn.hidden = !undo; btn.textContent = T("undo");
  btn.onclick = () => { tb.hidden = true; undo && undo(); };
  tb.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => (tb.hidden = true), 5000);
}
function newNote() {
  const b = day(current);
  const n = { id: uid(), text: "", ci: b.active.length % 7, w: 240, h: 206, x: 28, y: 28, created: nowIso() };
  b.active.push(n); save(); render(); focusNote(n.id);
}
function removeFrom(list, n) { const i = list.indexOf(n); if (i >= 0) list.splice(i, 1); return i; }
function completeNote(n) {
  const k = current, b = day(k), i = removeFrom(b.active, n);
  const a = { ...n, done_at: nowIso() }; b.archived.push(a); save(); render();
  toast(T("done_toast"), () => { removeFrom(b.archived, a); b.active.splice(i, 0, n); save(); render(); });
}
function deleteNote(n) {
  if (n.kind === "plan") return;
  const k = current, b = day(k), i = removeFrom(b.active, n);
  if (n.rid) skip(n.rid, k);
  save(); render();
  toast(T("deleted_toast"), () => { b.active.splice(i, 0, n); save(); render(); });
}
function moveNote(n, target) {
  if (target === current) return;
  const from = current, b = day(from), i = removeFrom(b.active, n);
  const copy = { ...n }; delete copy.fired;
  if (copy.rid) { skip(copy.rid, from); delete copy.rid; }
  day(target).active.push(copy); save(); render();
  toast(T("moved_toast", { d: inline(humanDate(parseKey(target))) }), () => { removeFrom(day(target).active, copy); b.active.splice(i, 0, n); save(); render(); });
}
function duplicate(n) {
  const c = { ...n, id: uid(), created: nowIso() };
  ["source", "yandex_uid", "kind", "fired", "remind", "rid"].forEach((k) => delete c[k]);
  day(current).active.push(c); save(); render();
}

// ---------- шторки ----------
function openSheet(title, body) {
  $("#sheet-title").textContent = title;
  const b = $("#sheet-body"); b.innerHTML = ""; b.appendChild(body);
  $("#sheet-wrap").hidden = false; $("#sheet").scrollTop = 0;
}
function closeSheet() { $("#sheet-wrap").hidden = true; }
function listBtn(icon, text, fn, cls) { const b = el("button", "list-btn" + (cls ? " " + cls : ""), (ICON[icon] || "") + `<span>${esc(text)}</span>`); b.onclick = fn; return b; }
function buttons(okText, ok) {
  const row = el("div", "btn-row"), c = el("button", "btn", esc(T("cancel"))), o = el("button", "btn primary", esc(okText));
  c.onclick = closeSheet; o.onclick = ok; row.append(c, o); return row;
}
function radio(text, on, fn) { const b = el("button", "radio" + (on ? " on" : ""), `<span class="r"></span><span class="grow">${esc(text)}</span>`); b.onclick = fn; return b; }

function noteMenu(n) {
  const body = el("div");
  body.appendChild(el("div", "section", esc(T("m_color"))));
  const sw = el("div", "swatches");
  palette().colors.forEach((c, i) => {
    const s = el("button", "swatch" + (n.ci === i ? " on" : "")); s.style.setProperty("--c", c); s.setAttribute("aria-label", palette().names[LANG === "ru" ? 0 : 1][i]);
    s.onclick = () => { n.ci = i; if (n.rid && template(n.rid)) template(n.rid).ci = i; save(); render(); closeSheet(); };
    sw.appendChild(s);
  });
  body.appendChild(sw);
  body.appendChild(listBtn("bell", T("m_reminder"), () => reminderSheet(n)));
  if (n.kind !== "plan") body.appendChild(listBtn("repeat", T("m_repeat"), () => repeatSheet(n)));
  if (n.kind === "plan") body.appendChild(listBtn("move", T("m_open_tomorrow"), () => { closeSheet(); showDay(keyOf(addDays(parseKey(current), 1))); }));
  if (current !== todayKey()) body.appendChild(listBtn("today", T("m_move_today"), () => { closeSheet(); moveNote(n, todayKey()); }));
  body.appendChild(listBtn("move", T("m_move_to"), () => moveSheet(n)));
  body.appendChild(listBtn("copy", T("m_duplicate"), () => { closeSheet(); duplicate(n); }));
  if (n.kind !== "plan") body.appendChild(listBtn("trash", T("m_delete"), () => { closeSheet(); deleteNote(n); }, "danger"));
  openSheet(n.text.split("\n")[0].slice(0, 40) || T("new_note"), body);
}

function monthGrid(selKey, onPick) {
  const box = el("div");
  let view = parseKey(selKey); view = new Date(view.getFullYear(), view.getMonth(), 1);
  const draw = () => {
    box.innerHTML = "";
    const nav = el("div", "month-nav"), p = el("button", "", "‹"), nx = el("button", "", "›");
    nav.append(p, el("b", "", `${MONTHS_NOM[LANG][view.getMonth()]} ${view.getFullYear()}`), nx);
    p.onclick = () => { view = new Date(view.getFullYear(), view.getMonth() - 1, 1); draw(); };
    nx.onclick = () => { view = new Date(view.getFullYear(), view.getMonth() + 1, 1); draw(); };
    const g = el("div", "mgrid");
    WD_SHORT[LANG].forEach((w) => g.appendChild(el("div", "h", w)));
    const start = addDays(view, -wd(view));
    for (let i = 0; i < 42; i++) {
      const x = addDays(start, i), k = keyOf(x);
      const c = el("button", "c" + (x.getMonth() !== view.getMonth() ? " other" : "") + (k === todayKey() ? " today" : "") + (k === selKey ? " sel" : "") + (peek(k).active.length ? " has" : ""),
        `<span class="dd">${x.getDate()}</span><span class="dot"></span>`);
      c.onclick = () => { selKey = k; onPick(k); draw(); };
      g.appendChild(c);
    }
    box.append(nav, g);
  };
  draw();
  return box;
}
function monthSheet() { openSheet(T("calendar"), monthGrid(current, (k) => { closeSheet(); showDay(k); })); }
function moveSheet(n) {
  const body = el("div"), td = parseKey(todayKey());
  let sel = keyOf(addDays(parseKey(current), 1));
  const chips = el("div", "chips");
  const toMon = (8 - (wd(td) + 1)) % 7 || 7;
  [[T("tomorrow"), 1], [T("q_day_after"), 2], [T("q_monday"), toMon], [T("q_week"), 7]].forEach(([t, d]) => {
    const c = el("button", "chip", esc(t)); c.onclick = () => { sel = keyOf(addDays(td, d)); grid.replaceWith(grid = monthGrid(sel, (k) => (sel = k))); }; chips.appendChild(c);
  });
  let grid = monthGrid(sel, (k) => (sel = k));
  body.append(chips, grid, buttons(T("move_btn"), () => { closeSheet(); moveNote(n, sel); }));
  openSheet(T("move_title"), body);
}
function reminderSheet(n) {
  const body = el("div"), now = new Date();
  let [mode, times] = defaultReminder(parseKey(current), parseIso(n.created), now);
  if (n.remind && n.remind.times && n.remind.times.length) { times = [...n.remind.times]; mode = times.length > 1 ? "twice" : "once"; }
  else if (!n.remind && false) mode = "off";
  const mk = (v) => { const i = el("input"); i.type = "time"; i.value = v; return i; };
  const tm = mk(mode === "twice" ? times[0] : cfg.remind_morning), te = mk(mode === "twice" ? times[times.length - 1] : cfg.remind_evening), to = mk(mode === "once" ? times[0] : cfg.remind_evening);
  const opts = el("div");
  const draw = () => {
    opts.innerHTML = "";
    const r1 = radio(T("rem_twice"), mode === "twice", () => { mode = "twice"; draw(); }); const w1 = el("div", "row"); w1.append(tm, te); r1.appendChild(w1);
    const r2 = radio(T("rem_once"), mode === "once", () => { mode = "once"; draw(); }); r2.appendChild(to);
    const r3 = radio(T("rem_off"), mode === "off", () => { mode = "off"; draw(); });
    [tm, te, to].forEach((i) => i.addEventListener("click", (e) => e.stopPropagation()));
    opts.append(r1, r2, r3);
  };
  draw();
  const created = parseIso(n.created);
  const hint = el("p", "hint-text", esc((created && keyOf(created) === current && created.getHours() >= 12 ? T("rem_hint_after12") : T("rem_hint_twice")) + " " + T(NATIVE ? "rem_hint_native" : "rem_hint_mobile")));
  body.append(opts, hint, buttons(T("save"), () => {
    if (mode === "off") delete n.remind;
    else n.remind = { mode, times: mode === "twice" ? [...new Set([tm.value, te.value])].filter(Boolean).sort() : [to.value].filter(Boolean), since: nowIso() };
    n.fired = [];
    if (n.rid && template(n.rid)) template(n.rid).times = n.remind ? [...n.remind.times] : [];
    save(true); closeSheet(); render(); askNotify();
  }));
  openSheet(T("rem_title"), body);
}
function repeatSheet(n) {
  const t = n.rid ? template(n.rid) : null, d = parseKey(current);
  let kind = t ? t.rule.kind : "none";
  const chosen = new Set(t && t.rule.kind === "days" ? t.rule.days : [wd(d)]);
  const body = el("div"), opts = el("div");
  const draw = () => {
    opts.innerHTML = "";
    [["none", T("rep_none")], ["daily", T("rep_daily")], ["weekdays", T("rep_weekdays")], ["days", T("rep_days")]].forEach(([k, txt]) => opts.appendChild(radio(txt, kind === k, () => { kind = k; draw(); })));
    const dc = el("div", "chips daychips");
    WD_SHORT[LANG].forEach((w, i) => { const c = el("button", "chip" + (chosen.has(i) ? " on" : ""), esc(w)); c.onclick = () => { chosen.has(i) ? chosen.delete(i) : chosen.add(i); kind = "days"; draw(); }; dc.appendChild(c); });
    opts.appendChild(dc);
    opts.appendChild(radio(T("rep_monthly", { n: d.getDate() }), kind === "monthly", () => { kind = "monthly"; draw(); }));
  };
  draw();
  body.append(opts, el("p", "hint-text", esc(T("rep_hint", { d: inline(humanDate(d)) }))), buttons(T("save"), () => {
    if (kind === "none" || (kind === "days" && !chosen.size)) { if (n.rid) recurring = recurring.filter((x) => x.id !== n.rid); delete n.rid; }
    else n.rid = setRule(n, current, kind === "days" ? { kind, days: [...chosen] } : kind === "monthly" ? { kind, dom: d.getDate() } : { kind });
    save(true); closeSheet(); render();
  }));
  openSheet(T("rep_title"), body);
}
function archiveSheet() {
  const body = el("div"), b = day(current);
  if (!b.archived.length) body.appendChild(el("p", "hint-text", esc(T("archive_empty"))));
  [...b.archived].reverse().forEach((a) => {
    const w = el("div", "card-wrap"), c = el("div", "card");
    c.style.setProperty("--c", noteColor(a.ci));
    c.appendChild(el("div", "t", esc(a.text.trim() || T("empty"))));
    const act = el("div", "a"), r = el("button", "", esc(T("restore"))), x = el("button", "", esc(T("delete")));
    r.onclick = () => { removeFrom(b.archived, a); const n = { ...a }; delete n.done_at; b.active.push(n); save(true); render(); archiveSheet(); };
    x.onclick = () => { removeFrom(b.archived, a); save(true); render(); archiveSheet(); };
    act.append(r, x); c.appendChild(act); w.appendChild(c); body.appendChild(w); tear(c, hash(a.id), 2);
  });
  openSheet(T("done_title"), body);
}
function searchSheet() {
  const body = el("div"), inp = el("input"), res = el("div");
  inp.type = "search"; inp.placeholder = T("search_ph");
  const run = () => {
    const q = inp.value.trim().toLowerCase(); res.innerHTML = ""; if (!q) return;
    const hits = [];
    for (const k of Object.keys(days).filter(parseKey).sort().reverse())
      for (const [arch, list] of [[false, days[k].active], [true, days[k].archived]])
        for (const n of list) if (n.text.toLowerCase().includes(q)) hits.push({ k, arch, n });
    if (!hits.length) res.appendChild(el("p", "hint-text", esc(T("nothing_found"))));
    hits.slice(0, 60).forEach((h) => {
      const b = el("button", "result", `<div class="w">${esc(humanDate(parseKey(h.k)) + (h.arch ? T("archive_suffix") : ""))}</div><div class="x">${esc(h.n.text.replace(/\s+/g, " "))}</div>`);
      b.onclick = () => { closeSheet(); showDay(h.k); if (h.arch) archiveSheet(); else setTimeout(() => focusNote(h.n.id), 50); };
      res.appendChild(b);
    });
  };
  inp.addEventListener("input", run);
  body.append(inp, res);
  openSheet(T("search"), body);
  setTimeout(() => inp.focus(), 200);
}
function settingsSheet() {
  const body = el("div");
  const sel = (label, options, value, fn) => {
    const row = el("div", "row"), s = el("select");
    options.forEach(([v, t]) => { const o = el("option", "", esc(t)); o.value = v; o.selected = String(v) === String(value); s.appendChild(o); });
    s.onchange = () => fn(s.value); row.append(el("label", "", esc(label)), s); return row;
  };
  const time = (label, key) => { const row = el("div", "row"), i = el("input"); i.type = "time"; i.value = cfg[key]; i.onchange = () => { cfg[key] = i.value; saveCfg(); }; row.append(el("label", "", esc(label)), i); return row; };
  const toggle = (label, key, fn) => { const row = el("div", "row"), t = el("button", "toggle" + (cfg[key] ? " on" : "")); t.onclick = () => { cfg[key] = !cfg[key]; t.classList.toggle("on", cfg[key]); saveCfg(); fn && fn(); }; row.append(el("label", "", esc(label)), t); return row; };
  const refresh = () => { saveCfg(); LANG = cfg.lang; applyTheme(); translateStatic(); render(); settingsSheet(); };
  body.appendChild(el("div", "section", esc(T("set_look"))));
  body.appendChild(sel(T("set_lang"), [["ru", "Русский"], ["en", "English"]], cfg.lang, (v) => { cfg.lang = v; refresh(); }));
  body.appendChild(sel(T("set_theme"), [["auto", T("theme_auto")], ["light", T("theme_light")], ["dark", T("theme_dark")]], cfg.theme, (v) => { cfg.theme = v; refresh(); }));
  body.appendChild(sel(T("set_palette"), Object.entries(PALETTES).map(([k, p]) => [k, p.name[LANG === "ru" ? 0 : 1]]), cfg.palette, (v) => { cfg.palette = v; refresh(); }));
  body.appendChild(sel(T("set_font"), FONTS.map((f) => [f[0], f[0]]), cfg.font, (v) => { cfg.font = v; cfg.size = (FONTS.find((f) => f[0] === v) || FONTS[0])[2]; refresh(); }));
  body.appendChild(sel(T("set_size"), [14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 26].map((x) => [x, x + " px"]), cfg.size, (v) => { cfg.size = +v; refresh(); }));
  body.appendChild(toggle(T("set_flowers"), "flowers", applyTheme));
  body.appendChild(el("div", "section", esc(T("set_reminders"))));
  body.append(time(T("set_morning"), "remind_morning"), time(T("set_evening"), "remind_evening"), time(T("set_plan"), "plan_time"));
  body.appendChild(el("p", "hint-text", esc(T("set_plan_hint"))));
  if (NATIVE) {
    body.appendChild(listBtn("bell", T("set_notify"), () => askNotify()));
  } else if ("Notification" in window) {
    const st = Notification.permission;
    body.appendChild(st === "granted" ? el("p", "hint-text", esc(T("notify_on"))) : st === "denied" ? el("p", "hint-text", esc(T("notify_denied")))
      : listBtn("bell", T("set_notify"), () => Notification.requestPermission().then(() => settingsSheet())));
  }
  body.appendChild(el("div", "section", esc(T("set_data"))));
  body.appendChild(listBtn("copy", T("export"), exportData));
  body.appendChild(listBtn("move", T("import"), () => $("#import-file").click()));
  body.appendChild(el("p", "hint-text", esc(T("data_hint"))));
  if (!NATIVE) body.appendChild(el("p", "hint-text", esc(T("install_hint"))));
  openSheet(T("settings"), body);
}
async function exportData() {
  if (NATIVE && PL.Filesystem && PL.Share) {
    try {
      const name = `notes-${todayKey()}.json`;
      const res = await PL.Filesystem.writeFile({ path: name, data: JSON.stringify(serialize(), null, 2), directory: "CACHE", encoding: "utf8" });
      await PL.Share.share({ title: T("app"), files: [res.uri] });
      toast(T("exported"));
    } catch (e) { if (!String(e).includes("cancel")) toast(String(e.message || e)); }
    return;
  }
  const blob = new Blob([JSON.stringify(serialize(), null, 2)], { type: "application/json" });
  const a = el("a"); a.href = URL.createObjectURL(blob); a.download = ".stickies_data.json"; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}
function importData(file) {
  const fr = new FileReader();
  fr.onload = () => {
    try {
      const d = normalizeData(JSON.parse(fr.result)); let added = 0;
      for (const [k, v] of Object.entries(d.days)) {
        const b = day(k), ids = new Set([...b.active, ...b.archived].map((n) => n.id));
        v.active.forEach((n) => { if (!ids.has(n.id)) { b.active.push(n); added++; } });
        v.archived.forEach((n) => { if (!ids.has(n.id)) b.archived.push(n); });
      }
      d.recurring.forEach((t) => { if (!template(t.id)) recurring.push(t); });
      save(true); render(); closeSheet(); toast(T("imported", { n: added }));
    } catch (e) { toast(T("import_fail")); }
  };
  fr.readAsText(file);
}

// ---------- уведомления ----------
const SNOOZE = 10;
function askNotify() {
  if (NATIVE) { PL.LocalNotifications && PL.LocalNotifications.requestPermissions().catch(() => {}); return; }
  if ("Notification" in window && Notification.permission === "default") Notification.requestPermission();
}
function showPopup(n, dk, when) {
  const wrap = el("div", "popup-wrap"), p = el("div", "popup");
  p.style.setProperty("--c", noteColor(n.ci));
  p.innerHTML = `<div class="ph"><b>${esc(T("popup_title"))}</b><span class="meta bell">${ICON.bell}${esc(when)}</span><button class="px" aria-label="${esc(T("popup_close"))}">✕</button></div><div class="txt">${esc(n.text.trim() || T("empty"))}</div>`;
  p.querySelector(".px").onclick = () => wrap.remove();
  const pa = el("div", "pa");
  const act = (txt, fn) => { const b = el("button", "", esc(txt)); b.onclick = () => { wrap.remove(); fn(); }; pa.appendChild(b); };
  act(T("popup_done"), () => { const b = day(dk), list = b.active, x = list.find((q) => q.id === n.id); if (x) { removeFrom(list, x); b.archived.push({ ...x, done_at: nowIso() }); save(true); render(); } });
  act(T("popup_snooze", { n: SNOOZE }), () => { const x = day(dk).active.find((q) => q.id === n.id); if (x && x.remind) { const s = new Date(Date.now() + SNOOZE * 60e3); x.remind.snooze = `${keyOf(s)}T${fmtHM(s.getHours(), s.getMinutes())}:00`; save(true); render(); } });
  act(T("popup_open"), () => { showDay(dk); setTimeout(() => focusNote(n.id), 60); });
  p.appendChild(pa); wrap.appendChild(p); $("#popups").appendChild(wrap); tear(p, hash(n.id));
  if (navigator.vibrate && navigator.userActivation && navigator.userActivation.hasBeenActive) navigator.vibrate([120, 60, 120]);
  if ("Notification" in window && Notification.permission === "granted" && document.visibilityState !== "visible") {
    navigator.serviceWorker && navigator.serviceWorker.ready.then((r) => r.showNotification(T("popup_title") + " · " + when, { body: n.text, icon: "icons/icon-192.png", tag: n.id, data: { dk, id: n.id } })).catch(() => {});
  }
}
function checkReminders() {
  const now = new Date(), tk = keyOf(now); let shown = 0;
  for (const n of [...day(tk).active]) {
    const [due, snoozed] = dueReminders(n, tk, now);
    if (!due.length && !snoozed) continue;
    n.fired = [...(n.fired || []), ...due].filter((f) => f.startsWith(tk)).slice(-12);
    if (snoozed && n.remind) delete n.remind.snooze;
    showPopup(n, tk, due.length ? due[due.length - 1].split(" ")[1] : fmtHM(now.getHours(), now.getMinutes()));
    shown++;
  }
  if (shown) { save(true); if (current === tk) render(); }
}
// Системные уведомления (Android): планируем напоминания на неделю вперёд.
let nativeTimer = null;
function scheduleNative() {
  if (!NATIVE || !PL.LocalNotifications) return;
  clearTimeout(nativeTimer);
  nativeTimer = setTimeout(async () => {
    const LN = PL.LocalNotifications, now = new Date(), list = [];
    let changed = false;
    for (let i = 0; i < 7; i++) {
      const dk = keyOf(addDays(now, i));
      if (materialize(dk)) changed = true;
      for (const n of peek(dk).active) {
        if (!n.remind) continue;
        const since = parseIso(n.remind.since) || new Date(0), fired = new Set(n.fired || []);
        const times = [...(n.remind.times || [])];
        for (const t of times) {
          const hm = parseHM(t); if (!hm) continue;
          const at = parseKey(dk); at.setHours(hm[0], hm[1], 0, 0);
          if (at <= now || at <= since || fired.has(`${dk} ${fmtHM(hm[0], hm[1])}`)) continue;
          list.push({ at, t, n, dk });
        }
        const sn = parseIso(n.remind.snooze);
        if (sn && sn > now) list.push({ at: sn, t: fmtHM(sn.getHours(), sn.getMinutes()), n, dk });
      }
    }
    if (changed) { try { localStorage.setItem(DATA_KEY, JSON.stringify(serialize())); } catch (e) {} }
    list.sort((a, b) => a.at - b.at);
    try {
      const pending = await LN.getPending();
      if (pending.notifications && pending.notifications.length) await LN.cancel({ notifications: pending.notifications.map((x) => ({ id: x.id })) });
      if (list.length) await LN.schedule({ notifications: list.slice(0, 60).map((x) => ({
        id: hash(x.n.id + x.dk + x.t) % 2000000000,
        title: T("popup_title") + " · " + x.t,
        body: (x.n.text || "").trim() || T("empty"),
        schedule: { at: x.at, allowWhileIdle: true },
        smallIcon: "ic_stat_note", iconColor: "#74503A",
        extra: { dk: x.dk, id: x.n.id },
      })) });
    } catch (e) { console.warn("notifications", e); }
  }, 800);
}
function initNative() {
  if (!NATIVE) return;
  document.querySelectorAll('link[href*="fonts.googleapis"]').forEach((l) => l.remove());
  const css = document.createElement("link"); css.rel = "stylesheet"; css.href = "fonts/fonts.css"; document.head.appendChild(css);
  const LN = PL.LocalNotifications;
  if (LN) {
    LN.requestPermissions().catch(() => {});
    LN.addListener("localNotificationActionPerformed", (ev) => {
      const ex = (ev.notification && ev.notification.extra) || {};
      if (ex.dk) { showDay(ex.dk); setTimeout(() => focusNote(ex.id), 120); }
    });
  }
  if (PL.App) {
    PL.App.addListener("backButton", () => {
      if (!$("#sheet-wrap").hidden) closeSheet();
      else if (current !== todayKey()) showDay(todayKey());
      else PL.App.minimizeApp();
    });
    PL.App.addListener("resume", () => { tick(); scheduleNative(); });
  }
  scheduleNative();
}

let lastDay = todayKey();
function tick() {
  if (todayKey() !== lastDay) { const was = current === lastDay; lastDay = todayKey(); ensurePlan(); if (materialize(lastDay)) save(true); if (was) current = lastDay; render(); }
  checkReminders();
}

// ============================ запуск ============================
function init() {
  load(); LANG = cfg.lang;
  applyTheme(); translateStatic();
  $("#flowers").innerHTML = flowersSVG();
  tear($(".paper-head"), 202);
  ensurePlan();
  if (materialize(current)) save(true);
  render();
  $("#fab").onclick = newNote;
  $("#btn-today").onclick = () => showDay(todayKey());
  $("#btn-month").onclick = monthSheet;
  $("#week-prev").onclick = () => { weekStart = addDays(weekStart, -7); showDay(keyOf(weekStart)); };
  $("#week-next").onclick = () => { weekStart = addDays(weekStart, 7); showDay(keyOf(weekStart)); };
  $("#btn-search").onclick = searchSheet;
  $("#btn-archive").onclick = archiveSheet;
  $("#btn-settings").onclick = settingsSheet;
  $("#sheet-backdrop").onclick = closeSheet;
  $("#carry").onclick = () => { const n = carryOverdue(); showDay(todayKey()); toast(T("carried", { n })); };
  $("#import-file").onchange = (e) => { if (e.target.files[0]) importData(e.target.files[0]); e.target.value = ""; };
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if (cfg.theme === "auto") applyTheme(); });
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") tick(); else save(true); });
  window.addEventListener("pagehide", () => save(true));
  setInterval(tick, 20000); setTimeout(checkReminders, 1500);
  if (!NATIVE && "serviceWorker" in navigator && location.protocol !== "file:") navigator.serviceWorker.register("sw.js").catch(() => {});
  initNative();
}
document.addEventListener("DOMContentLoaded", init);
