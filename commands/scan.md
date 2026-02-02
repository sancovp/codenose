---
description: Scan a file or directory for code smells
argument-hint: <path>
allowed-tools:
  - Bash
  - Read
---

# CodeNose Scan

Scan the specified path for code smells using the CodeNose library.

Run this command to scan:
```bash
python3 -c "
from codenose import CodeNose
nose = CodeNose()
result = nose.scan('$ARGUMENTS')
if hasattr(result, 'smells'):
    print(nose.format_output(result) if result.smells else 'No smells detected!')
else:
    print(f'Scanned {result.total_files} files, {result.files_with_smells} with smells')
    print(f'Cleanliness: {result.cleanliness_score:.1%}')
    for t, c in result.by_type.items(): print(f'  {t}: {c}')
"
```

Report the results to the user.
