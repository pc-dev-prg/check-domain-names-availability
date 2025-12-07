# Check Domain Names Availability

Tento nástroj slouží ke kontrole dostupnosti domén na základě seznamu názvů uvedených v textovém souboru. Umožňuje kontrolovat více koncovek najednou, barevně zobrazovat výsledky v terminálu, zpomalit whois dotazy, a výsledky exportovat do CSV, JSON i barevného HTML.

---

## ✨ Funkce

- 📂 **Vstupní soubor** – výchozí `domains.txt` (lze změnit parametrem)
- 🔄 **Kontrola více TLD** – například `.cz .com .net`
- 🎨 **Barevný terminálový výstup** – volné domény zeleně, obsazené červeně
- 🐢 **Rate limiting (`--delay`)** – možnost zpomalit whois dotazy, abys předešel blokaci
- ⚡ **Multithreading (`--threads`)** – rychlejší kontrola velkého množství domén
- 📊 **Exporty**:
  - CSV (výchozí)
  - JSON (`--json`)
  - Barevné HTML (`--html`)
- 🔍 **Filtrování výsledků** – třeba pouze volné domény (`--only-free`)
  
---

## 📁 Struktura projektu

```
Check-domain-names-availability/
│
├── check_domains.py        # hlavní skript
├── domains.txt             # seznam názvů domén (jeden název na řádek)
└── README.md               # tento přehled
```

---

## 🚀 Instalace a nastavení prostředí

Níže jsou uvedeny různé způsoby, jak nainstalovat závislosti a připravit prostředí pro spuštění nástroje. Vyber si ten, který ti nejlépe vyhovuje:

### 1️⃣ Doporučené: Virtuální prostředí (venv)

Použití izolovaného virtuálního prostředí je nejbezpečnější a nejčistší způsob, jak spravovat závislosti projektu, aniž by došlo ke konfliktům s globálními balíčky.

#### Kroky:

1. Vytvoř virtuální prostředí ve složce projektu:

```bash
python3 -m venv .venv
```

2. Aktivuj ho:

- macOS / Linux (bash, zsh):

```bash
source .venv/bin/activate
```

- fish:

```bash
source .venv/bin/activate.fish
```

- Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

3. Aktualizuj pip a nainstaluj závislosti:

```bash
python -m pip install --upgrade pip
python -m pip install python-whois colorama
```

> Po skončení práce deaktivuj prostředí příkazem `deactivate`.

---

### 2️⃣ Alternativa: Instalace do uživatelského profilu

Pokud nechceš nebo nemůžeš používat virtuální prostředí, můžeš nainstalovat potřebné balíčky lokálně pro uživatele.

```bash
python3 -m pip install --user python-whois colorama
```

Poté se ujisti, že adresář `~/.local/bin` je přidán v proměnné prostředí PATH, aby bylo možné spouštět skripty.

---

### 3️⃣ Automatizované nastavení pomocí `setup.sh`

Pokud chceš rychle připravit prostředí a nainstalovat závislosti, můžeš použít skript `setup.sh`, který:

- vytvoří `.venv`, pokud neexistuje
- aktivuje virtuální prostředí
- aktualizuje pip
- nainstaluje `python-whois` a `colorama`

Spuštění:

```bash
./setup.sh
```

> Nezapomeň udělit souboru spustitelnost: `chmod +x setup.sh`

---

### 4️⃣ Použití Makefile

Makefile poskytuje jednoduché příkazy pro nastavení a spuštění skriptu:

```bash
make setup      # vytvoří a připraví virtuální prostředí
make activate   # zobrazí instrukce pro aktivaci venv
make run        # spustí skript s defaultní koncovkou .cz
```

---

## 🧠 Kdy který způsob použít?

- **Virtuální prostředí (venv)** – ideální pro většinu uživatelů a vývojářů, kteří chtějí mít čisté a izolované prostředí.
- **Instalace do uživatelského profilu** – vhodné, pokud nemůžeš použít venv nebo chceš mít nástroj dostupný globálně pro uživatele.
- **`setup.sh`** – rychlé a automatizované nastavení, pokud chceš minimalizovat manuální kroky.
- **Makefile** – pohodlné pro opakované použití a automatizaci běžných úkolů.

---

## 🧠 Rychlé použití

### 1️⃣ Základní použití (default `domains.txt`):

```bash
python check_domains.py .cz
```

### 2️⃣ Více koncovek najednou:

```bash
python check_domains.py ".cz .com .net"
```

### 3️⃣ Export do CSV (výchozí), JSON a HTML:

```bash
python check_domains.py .cz --json --html
```

### 4️⃣ Rate limit (snížení frekvence whois dotazů):

```bash
python check_domains.py .cz --delay 1.0
```

---

## 🛠 Troubleshooting (časté problémy)

### 1) Chyba `externally-managed-environment` při instalaci pip

Tato chyba znamená, že systémový Python je spravovaný (např. Homebrew / OS) a pip instalaci zamítá, aby se nepoškodil systém. Řešení:

- Doporučeně: použij **virtuální prostředí** (viz výše). Nejbezpečnější a nejjednodušší.
- Alternativně: použij `--user` (viz výše), nebo `pipx` pro instalaci CLI nástrojů.
- Vyhýbej se `--break-system-packages` pokud nevíš, co děláš.


### 2) Knihovna `python-whois` dává různé chyby nebo vrací surový whois text

- WHOIS servery nejsou konzistentní napříč TLD. Některé (zejména ccTLD) vrací text s chybovým kódem místo strukturovaných dat. Skript tyto stavy zaznamená do pole `info` a obvykle je považuje za "pravděpodobně volné".
- Doporučení: pro kritické ověřování u konkrétní TLD použij registrátora (ruční kontrola) nebo vyšší `--delay` a menší `--threads`.


### 3) Registrátoři omezují/blokují rapidní dotazy

- Zvyšte `--delay` (např. 1–2 sekundy) a sniž `--threads` (např. 2–5).
- Přidej pauzy mezi dávkami kontrol, pokud kontroluješ tisíce položek.


### 4) Chceš přesnější výsledek bez WHOIS

- Můžeš doplnit DNS A/NS záznamovou kontrolu (zda doména má DNS záznamy). To není 100% (může být zaparkovaná bez DNS), ale je to doplňující indikátor. Pokud chceš, můžu takovou kontrolu přidat.


---

## 📦 Formát výsledků

Každý výstupní záznam obsahuje:

- `name` – základní název ze souboru
- `suffix` – koncovka (TLD)
- `domain` – složená doména
- `available` – True/False
- `info` – doplňující informace z whois

---

## 🎨 HTML výstup

Generovaný HTML soubor zvýrazní volné domény zeleně a obsazené červeně. Je to rychlé a pohodlné pro sdílení.

---

## 📬 Kontakt / Podpora

Chceš-li rozšířit nástroj (retry/backoff, DNS checky, progress bar, exporty), napiš issue nebo mě kontaktuj. Rád pomůžu.

---

## 🛠 Licence

MIT – používej, jak chceš.
