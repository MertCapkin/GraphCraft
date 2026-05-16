# GraphStack v4 — Cursor Prompts & Setup Guide

---

## 🔧 Cursor'a Kurulum (İlk Kez)

### Adım 1 — GraphStack'i projeye yükle

Terminalden (projenin kök dizininde). İşletim sistemine göre üç eşdeğer yol var:

**macOS / Linux (bash):**
```bash
git clone https://github.com/MertCapkin/graphstack /tmp/graphstack
bash /tmp/graphstack/install.sh
```

**Windows (PowerShell — Git Bash gerekmez):**
```powershell
git clone https://github.com/MertCapkin/graphstack $env:TEMP\graphstack
& $env:TEMP\graphstack\install.ps1 .
```

**Her platform (Python — shell tercihinden bağımsız):**
```bash
git clone https://github.com/MertCapkin/graphstack /path/to/graphstack
python -m graphstack install . --non-interactive
```

Bu komut şunları yapar:
- `.cursor/rules/graphstack.mdc` → Cursor her açılışta bunu otomatik okur
- `.cursor/skills/` → tüm rol dosyaları
- `orchestrator/` → Orchestrator ve Token Optimizer
- `handoff/` + `scripts/` → board ve state dosyaları
- `scripts/graphstack/` → Python helper paketi (bash ve PowerShell shim'leri buna delege eder)

### Adım 2 — Graphify'ı yükle ve grafiği oluştur

```bash
pip install -r requirements.txt
# veya doğrudan aynı pin ile:
pip install "graphifyy>=0.7,<0.9"
```

Cursor'da projeyi aç, chat'e yaz:
```
/graphify .
```

Bu işlem `graphify-out/GRAPH_REPORT.md` ve `graph.json` dosyalarını oluşturur.  
Büyük projelerde 1-2 dakika sürebilir, sonrası anında.

### Adım 3 — Başla

Yeni bir Cursor chat'i aç ve aşağıdaki promptlardan birini kullan.

> **Not:** `.cursor/rules/graphstack.mdc` dosyası Cursor tarafından otomatik yüklenir.
> Kurallar her chat'te aktif — ek bir şey yapman gerekmiyor.

---

## ⚡ Normal Kullanım — Tek Prompt

```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
[Ne yapmak istediğini buraya yaz — Türkçe veya İngilizce]
```

**Örnekler:**
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
Add email verification to the registration flow.
```
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
Login endpoint çok yavaş, performans sorununu bul ve düzelt.
```

Orchestrator Architect → Builder → Reviewer → QA → Ship döngüsünü otomatik yönetir.

---

## 🚀 Sıfırdan Yeni Proje (Bootstrap Modu)

Henüz hiç kod yoksa:

```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
This is a new project with no existing codebase.
[Projeyi tanımla: ne yapıyor, kime yönelik, hangi teknoloji]
```

**Örnek:**
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
This is a new project. I want to build a REST API for task management.
Users can create projects, add tasks, assign them, track progress.
Tech stack: TypeScript, Node.js, Express, PostgreSQL.
```

Bootstrapper tüm modülleri planlar, bağımlılık sırasını belirler,
her döngü için brief yazar. Her döngü sonrası grafı gerçek koddan günceller.

---

## 🔄 Oturum Devam Ettirme

Cursor'ı kapatıp yeniden açtıysan:
```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
Resume from last session.
```

---

## 🎭 Manuel Rol Aktivasyonu (İleri Düzey)

Belirli bir rolü elle çalıştırmak için:

### Architect (planlama)
```
Read .cursor/skills/architect/ARCHITECT.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
[Ne planlamak istediğini yaz]
```

### Builder (doğrudan build)
```
Read .cursor/skills/builder/BUILDER.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
Brief is in handoff/BRIEF.md. Start building.
```

### Reviewer (kod inceleme)
```
Read .cursor/skills/reviewer/REVIEWER.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
Review the changes in [dosya adı veya "the last git diff"].
```

### QA (davranış doğrulama)
```
Read .cursor/skills/qa/QA.md and follow it exactly.
Read orchestrator/TOKEN_OPTIMIZER.md for token rules.
Trace and verify [özellik adı].
```

### Ship (deploy hazırlığı)
```
Read .cursor/skills/ship/SHIP.md and follow it exactly.
Run the pre-ship checklist for task [task-id].
```

---

## 📋 Board Komutları (Terminal)

Üç biçim de eşdeğerdir. Shell tercihinize göre seçin.

**macOS / Linux (bash):**
```bash
bash scripts/board.sh status
bash scripts/board.sh new my-feature Add OAuth login support
bash scripts/board.sh claim my-feature builder
bash scripts/board.sh complete my-feature
bash scripts/board.sh log
```

**Windows (PowerShell):**
```powershell
.\scripts\board.ps1 status
.\scripts\board.ps1 new my-feature Add OAuth login support
.\scripts\board.ps1 claim my-feature builder
.\scripts\board.ps1 complete my-feature
.\scripts\board.ps1 log
```

**Cross-platform (Python):**
```bash
python -m graphstack board status
python -m graphstack board new my-feature Add OAuth login support
python -m graphstack board claim my-feature builder
python -m graphstack board complete my-feature
python -m graphstack board log
```

---

## 💡 İpuçları

- Her Orchestrator döngüsü için **yeni bir Cursor chat** aç — context temiz kalır
- `.cursor/rules/graphstack.mdc` otomatik yüklenir, elle okutman gerekmiyor
- Grafı büyük değişikliklerden sonra güncelle: `/graphify --update`
- `handoff/STATE.md` dosyasını silme — oturum geçmişin orada
- `handoff/board/` klasörünü commit'le — ekip arkadaşların board'u görsün
