# DigitalHygieneAuto

> Autonomous File & Download Organizer for Windows with Safe Transactions, Instant Rollback, and Background Real-Time Monitoring.

---

## ⚡ Quick Start

Open your terminal or command prompt in this directory (`d:\DigitalHygieneAuto`):

### 1. Preview planned moves safely (Dry Run)
```powershell
python main.py organize --dry-run
```
*Shows a table of every file that would be organized without modifying anything on disk.*

### 2. Organize files (Live Run)
```powershell
python main.py organize --run
```
*Instantly categorizes files into clean subdirectories (Documents, Media, Installers, Archives, Code, etc.) and records a transaction log.*

### 3. Oops! Roll back anytime (100% Undo)
```powershell
python main.py undo
```
*Rolls back the last organization batch, restoring every moved file back to its exact previous location.*

### 4. Background Real-Time Monitoring (Watcher)
```powershell
python main.py watch
```
*Silently monitors your Downloads folder in the background. As soon as any new browser download finishes, it classifies and files it away automatically.*

### 5. Automated Background Maintenance (Windows Task Scheduler)
```powershell
# Run automatic cleanup every 4 hours in the background
python main.py setup-task --interval 4

# To remove the scheduled task:
python main.py remove-task
```

---

## ⚙️ Customization (`config.yaml`)

You can edit `config.yaml` to adjust rules or add target folders:
- **Additional Target Folders**: Add your Desktop or project folders to `targets`.
- **Smart Keywords**: Add custom keyword rules (e.g. your company name, project codes).
- **Ignore Rules**: Exclude specific extensions, lock files, or temporary files.
