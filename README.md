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
flowchart TB
    %% Styling & Spacing
    classDef client fill:#161b22,stroke:#58a6ff,stroke-width:2px,color:#ffffff;
    classDef zone fill:#0d1117,stroke:#30363d,stroke-width:1.5px,color:#c9d1d9;
    classDef security fill:#161b22,stroke:#f85149,stroke-width:2px,color:#ffffff;
    classDef data fill:#161b22,stroke:#3fb950,stroke-width:2px,color:#ffffff;

    subgraph Ingestion [" 📥 INGESTION & FILESYSTEM OBSERVATION TIER "]
        direction LR
        Downloads["Downloads Folder<br/><sub>Transient Web Downloads</sub>"]:::client
        Desktop["Desktop Clutter<br/><sub>Unorganized Workspace Files</sub>"]:::client
        TempStaging["Temp Staging Area<br/><sub>Browser & Installer Caches</sub>"]:::client
    end

    subgraph Region1 [" ⚙️ REGION 1: EVENT REACTOR & DEBOUNCE ZONE "]
        direction TB
        Watchdog["Watchdog OS Event Observer<br/>• Non-Polling Windows API Hooks<br/>• Zero CPU Idle Footprint (<0.2%)"]:::client
        Debounce["Write-Stabilization Debouncer<br/>• 500ms Buffer for Active Browser Downloads<br/>• Open File Handle Lock Detection"]:::security
    end

    subgraph Region2 [" 🧠 REGION 2: CLASSIFICATION & DECISION MATRIX "]
        direction TB
        MIMEClassifier["MIME & Magic Byte Detector<br/>• Deep File Signature Identification"]:::client
        ResumeManager["Career Asset & Resume Manager<br/>• Automated CV Versioning & Timestamping<br/>• Master Portfolio Synchronizer"]:::client
        Pruner["Empty Directory Pruner<br/>• Safe Recursive Folder Pruning"]:::client
    end

    subgraph CentralTransit [" 🛡️ CENTRAL TRANSIT: TRANSACTION & SAFETY GATEWAY "]
        direction TB
        JournalGateway["Atomic Move Executor<br/><sub>Transactional Safe Relocation Engine</sub>"]:::security
        HistoryStore[("Reversible Audit Journal<br/>.history.json Ledger")]:::data
    end

    subgraph StorageVaults [" 📁 TARGET STRUCTURED STORAGE VAULTS "]
        direction LR
        VaultResumes["📁 Career & Resumes Archive"]:::data
        VaultDocs["📁 Structured Documents & PDFs"]:::data
        VaultMedia["📁 Media & Asset Vault"]:::data
        VaultDev["📁 Code & Development Projects"]:::data
    end

    %% Spacious Architectural Connections
    Downloads -------------> Watchdog
    Desktop ---------------> Watchdog
    TempStaging -----------> Watchdog

    Watchdog --------------> Debounce
    Debounce --------------> MIMEClassifier

    MIMEClassifier --------> ResumeManager
    MIMEClassifier --------> Pruner

    ResumeManager ---------> CentralTransit
    Pruner ----------------> CentralTransit

    JournalGateway -.->|Record Transaction SHA-256| HistoryStore

    JournalGateway --------> VaultResumes
    JournalGateway --------> VaultDocs
    JournalGateway --------> VaultMedia
    JournalGateway --------> VaultDev
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
