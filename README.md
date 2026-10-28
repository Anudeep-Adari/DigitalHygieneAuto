<div align="center">

# 🧹 DigitalHygieneAuto

### Autonomous Desktop Hygiene, Resume Management & Storage Reclamation Daemon
**Python 3.10+ • Watchdog Event-Driven • Reversible SQLite/JSON Journaling • Automated Scheduling**

<p align="center">
  <em>Real-time zero-polling file system sentry, automated Downloads/Desktop triage, and intelligent career asset versioning.</em>
</p>

<!-- Badges -->
<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" /></a>
  <a href="https://pypi.org/project/watchdog/"><img src="https://img.shields.io/badge/Engine-Watchdog_Events-009688?style=for-the-badge&logo=pypi&logoColor=white" alt="Watchdog" /></a>
  <a href="https://github.com/Anudeep-Adari/DigitalHygieneAuto"><img src="https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" /></a>
  <a href="https://coderabbit.ai"><img src="https://img.shields.io/badge/CodeRabbit-AI_Reviewed-FF5C00?style=for-the-badge&logo=coderabbit&logoColor=white" alt="CodeRabbit" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Event--Driven-8957E5?style=flat-square" />
  <img src="https://img.shields.io/badge/Operations-Journaled_%26_Reversible-10B981?style=flat-square" />
  <img src="https://img.shields.io/badge/Resource_Footprint-%3C_35MB_RAM-brightgreen?style=flat-square" />
</p>

---

</div>

## 📌 Architecture & Routing Pipeline

```mermaid
flowchart LR
    subgraph Ingestion ["📥 Ingestion Streams"]
        Downloads["Downloads Folder"]
        Desktop["Desktop Clutter"]
    end

    subgraph Daemon ["⚙️ Event Reactor (watcher.py)"]
        Watchdog["Watchdog File System Observer"]
        Debounce["Write-Stabilization Debouncer\n(500ms Window)"]
    end

    subgraph Classifier ["🧠 Decision Matrix (rules.py)"]
        MIME["MIME & Magic Type Resolution"]
        ExtMatch["Extension Routing Rules"]
        ResumeEngine["Resume & Career Asset Analyzer\n(resume_manager.py)"]
    end

    subgraph StorageHub ["🗂️ Antigravity Workspace Destination"]
        Resumes["📁 Career Assets / Master Resumes"]
        Docs["📁 Organized Documents & PDFs"]
        Media["📁 Media & Assets Archive"]
        Dev["📁 Source Code & Archives"]
    end

    subgraph Safety ["🛡️ Audit & Transaction Store"]
        Journal[("Reversible Transaction Journal\n.history.json")]
    end

    Ingestion --> Watchdog
    Watchdog --> Debounce
    Debounce --> Classifier
    Classifier --> StorageHub
    Classifier -.->|Audit Log & Rollback Pointer| Journal
```

---

## ⚡ Core Engineering Highlights

* **Real-Time Zero-Polling Observer:** Powered by operating system filesystem hooks via `watchdog`, consuming negligible CPU (<0.2%) and idling under 35MB RAM.
* **Write-Completion Debounce:** Waits for browser or installer file locks to fully release before initiating relocation, preventing corrupted partial downloads.
* **Semantic Resume Manager (`resume_manager.py`):** Automatically detects newly generated curriculum vitae, portfolio drafts, and interview prep PDFs, routing them into dedicated structured folders with timestamped revisions.
* **Safe Reversible Journaling:** Records previous absolute paths and SHA-256 hashes into `.history.json`, enabling single-command rollbacks if a file is relocated mistakenly.

---

## 🖥️ Live Terminal Interface Preview

```
================================================================================
  DigitalHygieneAuto v3.0  ─  Autonomous Workspace Sentry
================================================================================
  [STATUS] Active Daemon Running  │  [WATCHING] C:\Users\User\Downloads
  [UPTIME] 14d 08h 12m            │  [EVENTS PROCESSED] 1,482 files
--------------------------------------------------------------------------------
  [23:41:02] FILE_CREATED   -> Senior_DevOps_Resume_2026.pdf
  [23:41:03] CLASSIFIED     -> Career / Master Resumes [RULE_MATCH: ResumeRegex]
  [23:41:03] MOVED          -> G:\Career\Resumes\Senior_DevOps_Resume_2026.pdf
  [23:41:03] JOURNAL_ENTRY  -> Recorded transaction #1483 (Reversible: YES)
--------------------------------------------------------------------------------
```

---

## 🚀 Quickstart & Daemon Setup

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Anudeep-Adari/DigitalHygieneAuto.git
cd DigitalHygieneAuto

# Install Python requirements
pip install -r requirements.txt # watchdog, pyyaml
```

### 2. Configuration (`config.yaml`)

Define your target routing directories and cleanup rules:

```yaml
watch_paths:
  - "C:/Users/%USERNAME%/Downloads"
  - "C:/Users/%USERNAME%/Desktop"

destinations:
  resumes: "G:/Career/Resumes"
  documents: "G:/Documents/Archive"
  installers: "C:/Temp/Installers"

rules:
  delete_empty_folders: true
  auto_resume_versioning: true
  retention_days_temp: 14
```

### 3. Launching Daemon & Background Scheduler

```bash
# Run foreground watcher
python main.py

# Install as Windows Startup Scheduled Task
python scheduler_helper.py --install
```

---

<div align="center">

Crafted with high engineering precision by **[Anudeep Adari](https://github.com/Anudeep-Adari)**  
Continuous AI Code Reviews powered by **CodeRabbit**

</div>
