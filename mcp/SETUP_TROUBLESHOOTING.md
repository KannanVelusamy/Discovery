# MCP Server Setup & Troubleshooting

## ✅ Fixed: Virtual Environment Setup

The start script now automatically handles virtual environment creation and dependency installation.

---

## 🚀 Quick Start

Simply run:

```bash
cd /Users/kannan/DPAS/discovery/mcp
./start_mcp_server.sh
```

The script will:
1. ✅ Check Python installation
2. ✅ Create virtual environment (if needed)
3. ✅ Activate virtual environment
4. ✅ Install dependencies (httpx, mcp)
5. ✅ Start the MCP server

---

## 📋 What Changed

### Before (Causing Error):
```bash
# Tried to install globally - failed on externally-managed Python
pip3 install httpx mcp  # ❌ Error
```

### After (Fixed):
```bash
# Creates and uses virtual environment
python3 -m venv venv
source venv/bin/activate
pip install httpx mcp   # ✅ Works in venv
```

---

## 🔍 Understanding the Error

### Original Error:
```
error: externally-managed-environment
× This environment is externally managed
```

**Cause:** Python 3.13 installed via Homebrew on macOS prevents system-wide package installation to avoid breaking the OS Python environment.

**Solution:** Use a virtual environment (isolated Python environment for this project).

---

## 📦 Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment

```bash
cd /Users/kannan/DPAS/discovery/mcp
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install httpx>=0.27.0 mcp>=1.0.0
```

### 4. Run MCP Server

```bash
python entitlement_mcp.py
```

### 5. Deactivate When Done

```bash
deactivate
```

---

## 🧪 Verify Installation

After running the start script, verify everything is set up:

### Check Virtual Environment

```bash
cd /Users/kannan/DPAS/discovery/mcp
source venv/bin/activate
python --version  # Should show Python 3.13.3
which python      # Should point to venv/bin/python
```

### Check Installed Packages

```bash
pip list | grep -E "httpx|mcp"
```

Expected output:
```
httpx            0.27.x
mcp              1.x.x
```

### Test MCP Server

```bash
python entitlement_mcp.py
```

You should see:
```
🚀 Starting Entitlement MCP Server...
```

---

## 🐛 Common Issues

### Issue 1: Permission Denied

**Error:**
```
-bash: ./start_mcp_server.sh: Permission denied
```

**Solution:**
```bash
chmod +x start_mcp_server.sh
./start_mcp_server.sh
```

---

### Issue 2: Virtual Environment Already Exists

**Symptom:** Old or corrupted virtual environment

**Solution:**
```bash
cd /Users/kannan/DPAS/discovery/mcp
rm -rf venv
./start_mcp_server.sh  # Will recreate venv
```

---

### Issue 3: Python Not Found

**Error:**
```
python: command not found
```

**Solution:**
Ensure Python 3 is installed:
```bash
python3 --version  # Should show 3.8 or higher
```

If not installed:
```bash
brew install python@3
```

---

### Issue 4: Dependencies Won't Install

**Error:**
```
ERROR: Could not find a version that satisfies the requirement mcp
```

**Solution:**
Update pip first:
```bash
source venv/bin/activate
pip install --upgrade pip
pip install httpx mcp
```

---

### Issue 5: Module Not Found After Installation

**Error:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Cause:** Not using the virtual environment

**Solution:**
Always run via the start script, or manually activate venv:
```bash
cd /Users/kannan/DPAS/discovery/mcp
source venv/bin/activate
python entitlement_mcp.py
```

---

## 📂 Directory Structure

```
/Users/kannan/DPAS/discovery/mcp/
├── venv/                       ← Virtual environment (auto-created)
│   ├── bin/
│   │   ├── python             ← Isolated Python
│   │   └── activate           ← Activation script
│   └── lib/
│       └── python3.13/
│           └── site-packages/  ← Installed packages here
├── entitlement_mcp.py         ← MCP server code
├── start_mcp_server.sh        ← Start script (use this!)
├── README.md                  ← Documentation
└── .gitignore                 ← Git ignore (excludes venv)
```

---

## 🔧 Development Tips

### Activate Virtual Environment (for development)

```bash
cd /Users/kannan/DPAS/discovery/mcp
source venv/bin/activate
```

### Install Additional Packages

```bash
# Must be in activated venv
pip install package-name
```

### Freeze Dependencies

To save exact versions:
```bash
pip freeze > requirements.txt
```

### Install from Requirements

```bash
pip install -r requirements.txt
```

---

## 🎯 Expected Behavior

When you run `./start_mcp_server.sh`:

```
═══════════════════════════════════════════════════════════════
  🚀 Starting Entitlement MCP Server
═══════════════════════════════════════════════════════════════

✅ Python version: Python 3.13.3

✅ Virtual environment found

🔄 Activating virtual environment...
✅ Virtual environment activated

📦 Checking dependencies...
✅ All dependencies already installed

═══════════════════════════════════════════════════════════════
  📋 Configuration
═══════════════════════════════════════════════════════════════

  Profile API: https://localhost:8080/services/security/profile
  SSL Verification: Disabled (Development Mode)
  Virtual Environment: /Users/kannan/DPAS/discovery/mcp/venv

═══════════════════════════════════════════════════════════════
  🎯 MCP Server Ready
═══════════════════════════════════════════════════════════════

Starting entitlement MCP server...
Press Ctrl+C to stop

═══════════════════════════════════════════════════════════════

🚀 Starting Entitlement MCP Server...
```

---

## ✅ Summary

- ✅ **Virtual environment** - Isolated Python environment
- ✅ **Automatic setup** - Script handles everything
- ✅ **Dependencies** - httpx and mcp installed in venv
- ✅ **Clean separation** - Won't affect system Python
- ✅ **Git ignored** - venv/ excluded from version control

---

## 🚀 Next Steps

1. **Run the start script:**
   ```bash
   cd /Users/kannan/DPAS/discovery/mcp
   ./start_mcp_server.sh
   ```

2. **Verify it starts successfully** - You should see the startup logs

3. **Leave it running** - Keep the terminal window open

4. **In another terminal**, test the frontend authentication flow

---

**The virtual environment setup is now complete!** 🎉

Just run `./start_mcp_server.sh` and everything will be handled automatically.

