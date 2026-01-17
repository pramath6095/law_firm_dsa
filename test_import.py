#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

print("Testing core_logic import...")
try:
    import core_logic
    print("✓ core_logic imported successfully")
    print("✓ EventManager class exists:", hasattr(core_logic, 'EventManager'))
except Exception as e:
    print("✗ Import failed:")
    print(type(e).__name__, ":", e)
    import traceback
    traceback.print_exc()
