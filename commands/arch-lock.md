---
description: Toggle CodeNose architecture lock mode
allowed-tools:
  - Bash
  - Read
---

# Architecture Lock Toggle

Toggle CodeNose architecture lock mode. When enabled, writes to non-canonical filenames are blocked.

## Check current state:
```bash
test -f ~/.claude/.codenose_arch_lock && echo "ARCH LOCK: ON" || echo "ARCH LOCK: OFF"
```

## To enable:
```bash
mkdir -p ~/.claude && touch ~/.claude/.codenose_arch_lock
```

## To disable:
```bash
rm -f ~/.claude/.codenose_arch_lock
```

Tell the user the current state and ask if they want to toggle it.
