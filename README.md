# OmniRoute + Claude Code — High-Performance Multi-Model System

A production-grade configuration and tooling suite for pairing **OmniRoute** with **Claude Code**, enabling seamless multi-provider routing (Google Gemini, NVIDIA NIM, OpenCode) with automatic rate-limit rotation, cross-combo failovers, and custom autonomous coding skills.

---

## 🚀 Quick Setup (New Machine / Clone)

```bash
# 1. Run the master setup script
python setup_omniroute.py

# 2. Restart OmniRoute (to load SQLite middleware hooks)

# 3. Launch Claude Code
claude
```

---

## 📚 Complete Setup & Architecture Guide

For the full architectural breakdown, middleware hook source code, troubleshooting matrix, and database schemas:
👉 **[Read SETUP.md](SETUP.md)**

---

## 🛠️ Included Tools & Configurations

- **[`setup_omniroute.py`](setup_omniroute.py)**: 1-click bootstrap script that initializes SQLite middleware hooks, combo definitions, cross-combo fallback chains, and settings files.
- **[`refresh.py`](refresh.py)**: Live health check & auto-healing script that tests active models and promotes working ones during upstream outages.
- **[`SETUP.md`](SETUP.md)**: Exhaustive setup guide, error troubleshooting matrix, and configuration reference.
- **[`.claude/commands/`](.claude/commands/)**: 8 high-velocity autonomous coding skills (`/mega-build`, `/sprint`, `/fullstack`, `/fix`, `/refactor`, `/scan`, `/feature`, `/turbo`).
- **[`.claude/settings.example.json`](.claude/settings.example.json)**: Model combo environment configuration template.