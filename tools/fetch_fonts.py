"""Скачивает свободные шрифты (лицензия SIL OFL) для сборок в папку fonts/.

Google Fonts по запросу от неизвестного клиента отдаёт ссылки на файлы TTF —
их и берём. Заодно пишет fonts/fonts.css для мобильной версии.
Запуск: python tools/fetch_fonts.py [папка]
"""
import os
import re
import sys
import urllib.request

FAMILIES = [("Caveat", [400, 600]), ("Marck Script", [400]), ("Lora", [400, 500]),
            ("PT Sans", [400, 700]), ("PT Serif", [400])]
UA = "notes-fetch-fonts/1.0"  # неизвестному клиенту Google отдаёт TTF, а не WOFF2


def css_url(name, weights):
    fam = name.replace(" ", "+")
    if weights == [400]:
        return f"https://fonts.googleapis.com/css2?family={fam}"
    return f"https://fonts.googleapis.com/css2?family={fam}:wght@{';'.join(map(str, weights))}"


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")


def parse(css):
    """[(family, weight, url)] из CSS Google Fonts."""
    out = []
    for block in re.findall(r"@font-face\s*{(.*?)}", css, re.S):
        fam = re.search(r"font-family:\s*'([^']+)'", block)
        wt = re.search(r"font-weight:\s*(\d+)", block)
        url = re.search(r"url\((https://[^)]+)\)", block)
        if fam and wt and url:
            out.append((fam.group(1), int(wt.group(1)), url.group(1)))
    return out


def main(dest):
    os.makedirs(dest, exist_ok=True)
    faces = []
    for name, weights in FAMILIES:
        for fam, wt, url in parse(get(css_url(name, weights))):
            ext = os.path.splitext(url.split("?")[0])[1].lower() or ".ttf"
            if ext not in (".ttf", ".otf"):
                raise SystemExit(f"Ожидался TTF, получен {ext}: {url}")
            fname = f"{fam.replace(' ', '')}-{wt}{ext}"
            n = 2
            while any(x[2] == fname for x in faces):  # если файл разбит на части
                fname = f"{fam.replace(' ', '')}-{wt}-{n}{ext}"
                n += 1
            path = os.path.join(dest, fname)
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    f.write(get(url, binary=True))
            faces.append((fam, wt, fname))
            print("ok", fname)
    with open(os.path.join(dest, "fonts.css"), "w", encoding="utf-8") as f:
        for fam, wt, fname in faces:
            f.write(f"@font-face {{ font-family: '{fam}'; font-weight: {wt}; "
                    f"font-style: normal; font-display: swap; src: url('{fname}'); }}\n")
    with open(os.path.join(dest, "OFL.txt"), "w", encoding="utf-8") as f:
        f.write("Caveat, Marck Script, Lora, PT Sans, PT Serif — SIL Open Font License 1.1.\n"
                "https://openfontlicense.org\n")
    if not faces:
        raise SystemExit("Шрифты не получены")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fonts")
