# Process Simplification

## Current complexity drivers

- multiple startup entry points (`.bashrc`, `.xinitrc`, `systemd`)
- runtime mode hardcoded in code (`pyglet.options['headless'] = True`)
- mixed generations of dependency definitions (`requirements.txt` and `pyproject.toml`)

## Simplified target design

1. **Single launcher**
   - Introduce one CLI entrypoint selecting object + system.
2. **Single startup authority**
   - Use only `systemd` (no auto-`startx` from shell profile).
3. **Single dependency source**
   - Maintain only `pyproject.toml` + lockfile.
4. **Single media root policy**
   - Keep `/storage` optional by config flag instead of implicit path checks.

## Immediate low-risk wins

- Run `Entro.ai.py` / `Heads.ai.py` wrappers now for macOS testing.
- Use `Fountain.ai.py` for stable cross-platform audio testing.
- Keep original files untouched until behavior is validated on all nodes.

