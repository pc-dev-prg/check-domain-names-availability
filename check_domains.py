#!/usr/bin/env python3
"""
check_domains.py
Kontroluje dostupnost domén ze souboru.
Funkce:
 - defaultní soubor domains.txt (možno přepsat)
 - více koncovek najednou
 - barevný terminálový výstup
 - export do CSV (default), JSON (volitelně) a barevného HTML (volitelně)
 - rate limiter (--delay) pro snížení frekvence whois dotazů
 - multithreading (počet vláken lze nastavit)
 - volitelně zobrazit pouze volné (--only-free)
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import argparse
import csv
import json
import time
import whois
import threading
import sys

# colorama pro hezký terminál
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
except Exception:
    class _C:
        def __getattr__(self, _): return ""
    Fore = Style = _C()

DEFAULT_FILE = "domains.txt"
DEFAULT_CSV = "results.csv"
DEFAULT_HTML = "results.html"
DEFAULT_JSON = "results.json"

def parse_suffixes(s: str):
    parts = []
    for token in s.replace(",", " ").split():
        tok = token.strip()
        if not tok:
            continue
        if not tok.startswith("."):
            tok = "." + tok
        parts.append(tok.lower())
    return parts

class RateLimiter:
    """Ensures at least min_interval seconds between calls across threads."""
    def __init__(self, min_interval: float):
        self.min_interval = float(min_interval) if min_interval else 0.0
        self.lock = threading.Lock()
        self._last = 0.0

    def wait(self):
        if self.min_interval <= 0:
            return
        with self.lock:
            now = time.monotonic()
            diff = self.min_interval - (now - self._last)
            if diff > 0:
                time.sleep(diff)
                now = time.monotonic()
            self._last = now

def check_domain_whois(domain: str, rate_limiter: RateLimiter):
    """Do whois with global rate limiting. Returns dict."""
    rate_limiter.wait()
    try:
        w = whois.whois(domain)
        domain_name = getattr(w, "domain_name", None)
        if not domain_name:
            return {"domain": domain, "available": True, "info": "no whois data (likely available)"}
        return {"domain": domain, "available": False, "info": f"registered ({domain_name})"}
    except Exception as e:
        msg = str(e)
        low = msg.lower()
        if "no match" in low or "not found" in low or "no data found" in low or "domain not found" in low:
            return {"domain": domain, "available": True, "info": f"exception indicated free: {msg}"}
        # obecně považujeme chybu za indikaci možné volné domény, ale uložíme chybu do info
        return {"domain": domain, "available": True, "info": f"whois error (treated as available): {msg}"}

def worker(name: str, suffix: str, rate_limiter: RateLimiter):
    domain = f"{name}{suffix}"
    res = check_domain_whois(domain, rate_limiter)
    res["name"] = name
    res["suffix"] = suffix
    return res

def save_csv(rows, path: Path):
    fieldnames = ["name", "suffix", "domain", "available", "info"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "name": r.get("name",""),
                "suffix": r.get("suffix",""),
                "domain": r.get("domain",""),
                "available": r.get("available",""),
                "info": r.get("info","")
            })

def save_json(rows, path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

def save_html(rows, path: Path, title="Domain check results"):
    # jednoduché inline CSS, zeleně = volné, červeně = obsazené
    html = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'>",
        f"<title>{title}</title>",
        "<style>",
        "body{font-family:Arial,Helvetica,sans-serif;padding:16px}",
        "table{border-collapse:collapse;width:100%}",
        "th,td{border:1px solid #ddd;padding:8px;text-align:left}",
        "th{background:#f4f4f4}",
        ".free{background:#e6ffed;color:#034d21}",
        ".taken{background:#ffecec;color:#6b0000}",
        ".mono{font-family:monospace}",
        "</style></head><body>",
        f"<h1>{title}</h1>",
        f"<p>Generováno: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>",
        "<table>",
        "<thead><tr><th>Name</th><th>Suffix</th><th>Domain</th><th>Available</th><th>Info</th></tr></thead>",
        "<tbody>"
    ]
    for r in rows:
        cls = "free" if r.get("available") else "taken"
        html.append(
            "<tr>"
            f"<td>{r.get('name','')}</td>"
            f"<td>{r.get('suffix','')}</td>"
            f"<td class='mono'>{r.get('domain','')}</td>"
            f"<td class='{cls}'>{'YES' if r.get('available') else 'NO'}</td>"
            f"<td>{r.get('info','')}</td>"
            "</tr>"
        )
    html += ["</tbody></table></body></html>"]
    path.write_text("\n".join(html), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Kontrola dostupnosti domén ze souboru.")
    parser.add_argument("suffixes", nargs="?", help="Koncovka(y) domén, např. .cz nebo .com,.net nebo \".cz .com\"", default=None)
    parser.add_argument("--file","-f", help=f"Soubor s názvy (default: {DEFAULT_FILE})", default=DEFAULT_FILE)
    parser.add_argument("--csv","-c", help=f"Uložit CSV (default: {DEFAULT_CSV})", nargs="?", const=DEFAULT_CSV, default=DEFAULT_CSV)
    parser.add_argument("--json","-j", help="Uložit JSON (zadej jméno nebo použij --json pro default results.json)", nargs="?", const=DEFAULT_JSON, default=None)
    parser.add_argument("--html","-H", help="Vygenerovat HTML (zadej jméno nebo použij --html pro default results.html)", nargs="?", const=DEFAULT_HTML, default=None)
    parser.add_argument("--threads","-t", type=int, default=10, help="Počet vláken (default 10)")
    parser.add_argument("--delay","-d", type=float, default=0.5, help="Minimální zpoždění mezi whois dotazy v sekundách (globálně). Zvýš to, pokud registrátoři blokují.")
    parser.add_argument("--no-color", action="store_true", help="Vypnout barevný výstup v terminálu")
    parser.add_argument("--only-free", action="store_true", help="Vypisovat / ukládat pouze volné domény")
    args = parser.parse_args()

    if not args.suffixes:
        print("Chyba: zadej alespoň jednu koncovku (např. .cz nebo \".cz,.com\").")
        parser.print_usage()
        sys.exit(1)

    suffixes = parse_suffixes(args.suffixes)
    if not suffixes:
        print("Neplatné koncovky.")
        sys.exit(1)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Soubor '{file_path}' nenalezen.")
        sys.exit(1)

    names = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not names:
        print("Soubor je prázdný.")
        sys.exit(1)

    total = len(names) * len(suffixes)
    print(f"Kontroluji {total} kombinací ({len(names)} jmen × {len(suffixes)} koncovek) s delay={args.delay}s ...")

    rate_limiter = RateLimiter(args.delay)
    rows = []
    start = time.time()
    max_workers = max(1, min(args.threads, total))

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = []
        for name in names:
            for suf in suffixes:
                futures.append(ex.submit(worker, name, suf, rate_limiter))

        try:
            for f in as_completed(futures):
                r = f.result()
                # filtr pokud chceš pouze volné
                if args.only_free and not r.get("available"):
                    continue
                rows.append(r)
                domain = r["domain"]
                available = r["available"]
                info = r.get("info","")
                if args.no_color:
                    tag = "[VOLNÁ]" if available else "[OBSAZENÁ]"
                    print(f"{tag} {domain} — {info}")
                else:
                    if available:
                        print(f"{Fore.GREEN}[VOLNÁ]   {domain}{Style.RESET_ALL} — {info}")
                    else:
                        print(f"{Fore.RED}[OBSAZENÁ] {domain}{Style.RESET_ALL} — {info}")
        except KeyboardInterrupt:
            print("Přerušeno uživatelem.")
            ex.shutdown(wait=False)
            sys.exit(1)

    duration = time.time() - start

    # uložení CSV (pokud nevynecháno)
    if args.csv:
        csv_path = Path(args.csv)
        save_csv(rows, csv_path)
        print(f"Uloženo do CSV: {csv_path}")

    if args.json:
        json_path = Path(args.json)
        save_json(rows, json_path)
        print(f"Uloženo do JSON: {json_path}")

    if args.html:
        html_path = Path(args.html)
        save_html(rows, html_path, title="Domain check results")
        print(f"Uloženo do HTML: {html_path}")

    print(f"Hotovo za {duration:.1f}s — záznamů: {len(rows)} (z {total}).")

if __name__ == "__main__":
    main()