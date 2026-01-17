#!/usr/bin/env python3
"""Rebuild core_logic.py cleanly"""
import os

# Read the clean portion (before corruption at line 702)
with open('backend/core_logic.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find where NotificationManager ends (around line 701)
clean_lines = lines[:701]

# Write to new file
with open('backend/core_logic_rebuilt.py', 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

# Now append EventManager class from the standalone file
with open('backend/event_manager_class.py', 'r', encoding='utf-8') as f:
    event_manager_code = f.read()

with open('backend/core_logic_rebuilt.py', 'a', encoding='utf-8') as f:
    f.write('\n')
    f.write(event_manager_code)

print("✓ Created core_logic_rebuilt.py")

# Verify it compiles
import py_compile
try:
    py_compile.compile('backend/core_logic_rebuilt.py', doraise=True)
    print("✓ File compiles successfully")
    
    # Replace the old file
    os.replace('backend/core_logic.py', 'backend/core_logic_old_corrupted.py')
    os.replace('backend/core_logic_rebuilt.py', 'backend/core_logic.py')
    print("✓ Replaced core_logic.py with clean version")
except Exception as e:
    print(f"✗ Compilation failed: {e}")
