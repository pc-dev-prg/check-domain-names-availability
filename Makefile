# Check Domain Names Availability

Tento projekt umožňuje kontrolu dostupnosti doménových jmen.

---

## Instalace a Setup skripty

Níže najdete různé způsoby, jak nainstalovat a spustit projekt. Vyberte si ten, který vám nejvíce vyhovuje:

### 1. Použití virtuálního prostředí (venv)

Tento způsob je doporučený, pokud chcete mít izolované prostředí pouze pro tento projekt.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install python-whois colorama
```

### 2. Alternativní instalace do uživatelského profilu

Pokud nechcete používat virtuální prostředí, můžete nainstalovat závislosti přímo do svého uživatelského profilu:

```bash
python3 -m pip install --user --upgrade pip
python3 -m pip install --user python-whois colorama
```

Tento způsob je vhodný, pokud nechcete spravovat virtuální prostředí, ale může dojít ke konfliktům s jinými projekty.

### 3. Použití `setup.sh`

Pokud je v projektu dostupný skript `setup.sh`, můžete jej spustit, který automatizuje nastavení prostředí:

```bash
./setup.sh
```

Tento skript obvykle vytvoří virtuální prostředí a nainstaluje potřebné závislosti.

### 4. Použití `Makefile`

Pokud máte nainstalovaný `make`, můžete použít Makefile pro rychlé nastavení a spuštění:

- Pro nastavení prostředí a instalaci závislostí:

```bash
make setup
```

- Pro aktivaci virtuálního prostředí:

```bash
make activate
```

- Pro spuštění skriptu s kontrolou domén:

```bash
make run
```

---

### Kdy který postup použít?

- **Virtuální prostředí (venv)** – doporučeno pro většinu uživatelů, kteří chtějí izolovat závislosti projektu.
- **Instalace do uživatelského profilu** – pokud nechcete používat virtuální prostředí, ale chcete mít závislosti dostupné globálně pro uživatele.
- **`setup.sh`** – pokud je k dispozici a chcete automatizovat nastavení bez dalších příkazů.
- **`Makefile`** – pokud preferujete práci s make nástrojem a chcete rychle spouštět předdefinované příkazy.

---

Pokud máte jakékoliv dotazy nebo potřebujete pomoc, neváhejte se obrátit na autora projektu.