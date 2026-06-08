# AI Runtime Layer

This folder documents the non-destructive compatibility layer added for local macOS testing while keeping Raspberry Pi behavior as default.

## Added entrypoints

- `Entro.ai.py`
- `Heads.ai.py`
- `Fountain.ai.py`

Each entrypoint supports:

- `--system rpi` (default)
- `--system macos`

## Why wrappers

Original files are left untouched. The AI wrappers inject only runtime compatibility behavior and then delegate to original scripts.

