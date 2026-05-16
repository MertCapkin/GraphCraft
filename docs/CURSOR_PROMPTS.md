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
- `.cursor/commands/graphstack.md` → Slash menüsünde `/graphstack` komutu

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

**Önerilen (en az sürtünme):** Cursor'da projeyle birlikte yeni Composer/Agent aç —
`graphstack.mdc` `alwaysApply: true` olduğu için Kurallar zaten yüklü. Direkt olarak
hedefini yaz (**Türkçe veya İngilizce**). Asistanın ilk işi olarak yine Orchestrator Activation
(okuma + TOKEN_OPTIMIZER + graf) çalıştırması gerekir; senin her seferinde
`Read orchestrator/...` kopyalamana gerek yok.

**Slash komutu (istersen daha net başlatmak için):** Sohbete `/` yaz → **`graphstack`**
dosyası `.cursor/commands/graphstack.md` içeriğini enjekte eder (`/graphstack` çıkmıyorsa
Cursor'ı yeniden başlat).

**İsteğe bağlı klasik satır *(başka editör ya da garanti için):*** aşağıdaki blok hâlen geçerlidir.

```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
[Hedefini yaz]
```

> **Not:** `.cursor/rules/graphstack.mdc` her oturumda otomatik yüklenir; bu satır fazladan garanti için.

---

## ⚡ Örnek hedef yazıları (klasik bloğu atlarsan bile)

Orchestrator yine graf + handoff yüklemesini yapmak zorunda; senden sadece amaç gerek:

```
Kayıtta e-posta doğrulaması eklemek istiyorum.
```
```
Login endpoint çok yavaş — performansı bul ve düzelt.
```
```
Resume from last session.
```

Architect → Builder → Reviewer → QA → Ship zinciri kullanıcı etkileşimi olmadan yürür.

---

## 🚀 Sıfırdan Yeni Proje (Bootstrap Modu)

Henüz kod yoksa **sırf hedef yazman yeter**: `alwaysApply` kuralları etkin.
İstersen garanti olarak `/graphstack` komutunun ardından açıklamayı yaz.

```
Boş bir repo için REST API yazıyorum: kullanıcılar proje oluşturup görev atayabilecek.
TypeScript + Node + Express + PostgreSQL istiyorum. İlk fazda önce authentication.
```

**Klasik tam blok (yedek)**

```
Read orchestrator/ORCHESTRATOR.md and follow it exactly.
This is a new project with no existing codebase.
[Projeyi tanımla: amaç, kullanıcı, teknoloji]
```

Bootstrapper tüm modülleri planlar, bağımlılık sırasını belirler,
her döngü için brief yazar; her döngü sonunda güncellenmiş graf gerekli.

---

## 🔄 Oturum Devam Ettirme

Cursor'ı yeniden açtıktan sonra sadece:

```
Önceki GraphStack oturumundan devam et.
STATE.md ile board'daki yapılacaklara uy.
```

Gerekli güvence için hâlen şu blok kullanılabilir:

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

- Her Orchestrator döngüsünde mümkünse **yeni bir Cursor chat** aç — context temiz kalır
- Cursor slash menüsünde **`/graphstack`** kullanarak Orchestrator açılışını netleştir
- `.cursor/rules/graphstack.mdc` otomatik yüklenir, elle okutman gerekmiyor
- Grafı büyük değişikliklerden sonra güncelle: `/graphify --update`
- `handoff/STATE.md` dosyasını silme — oturum geçmişin orada
- `handoff/board/` klasörünü commit'le — ekip arkadaşların board'u görsün
