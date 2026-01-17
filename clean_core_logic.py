#!/usr/bin/env python3
"""Clean core_logic.py by removing null bytes and adding EventManager"""

# Read the corrupted file and remove null bytes
with open('backend/core_logic.py', 'rb') as f:
    content = f.read()

# Find where the null bytes start (should be after NotificationManager)
clean_content = content.split(b'\x00')[0]

# Write clean version
with open('backend/core_logic_fixed.py', 'wb') as f:
    f.write(clean_content)

# Now append EventManager class
with open('backend/event_manager_class.py', 'r', encoding='utf-8') as f:
    event_manager_code = f.read()

with open('backend/core_logic_fixed.py', 'a', encoding='utf-8') as f:
    f.write('\n' + event_manager_code)

print("✓ Cleaned core_logic.py and added EventManager")
