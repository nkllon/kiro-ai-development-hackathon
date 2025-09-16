#!/usr/bin/env python3
"""
Test what Python actually allows with circular imports
"""

# Test 1: Simple circular import
print("🧪 TESTING CIRCULAR IMPORTS")
print("=" * 40)

# Test 2: Create two modules that import each other
print("\n1. Creating modules with circular imports...")

# Module A
with open("module_a.py", "w") as f:
    f.write('''
# Module A
print("Loading module A...")

try:
    import module_b
    print("Module A: Successfully imported module_b")
except ImportError as e:
    print(f"Module A: Failed to import module_b: {e}")

def function_a():
    return "Function A called"

print("Module A loaded")
''')

# Module B  
with open("module_b.py", "w") as f:
    f.write('''
# Module B
print("Loading module B...")

try:
    import module_a
    print("Module B: Successfully imported module_a")
except ImportError as e:
    print(f"Module B: Failed to import module_a: {e}")

def function_b():
    return "Function B called"

print("Module B loaded")
''')

print("✅ Created module_a.py and module_b.py")

# Test 3: Try to import them
print("\n2. Testing circular import...")
try:
    import module_a
    print("✅ Successfully imported module_a")
    print(f"Function A result: {module_a.function_a()}")
except Exception as e:
    print(f"❌ Failed to import module_a: {e}")

try:
    import module_b
    print("✅ Successfully imported module_b")
    print(f"Function B result: {module_b.function_b()}")
except Exception as e:
    print(f"❌ Failed to import module_b: {e}")

# Test 4: Test more complex circular import
print("\n3. Testing more complex circular import...")

# Module C that imports D
with open("module_c.py", "w") as f:
    f.write('''
# Module C
print("Loading module C...")

try:
    from module_d import function_d
    print("Module C: Successfully imported function_d from module_d")
except ImportError as e:
    print(f"Module C: Failed to import from module_d: {e}")

def function_c():
    return "Function C called"

print("Module C loaded")
''')

# Module D that imports C
with open("module_d.py", "w") as f:
    f.write('''
# Module D
print("Loading module D...")

try:
    from module_c import function_c
    print("Module D: Successfully imported function_c from module_c")
except ImportError as e:
    print(f"Module D: Failed to import from module_c: {e}")

def function_d():
    return "Function D called"

print("Module D loaded")
''')

try:
    import module_c
    print("✅ Successfully imported module_c")
    print(f"Function C result: {module_c.function_c()}")
except Exception as e:
    print(f"❌ Failed to import module_c: {e}")

try:
    import module_d
    print("✅ Successfully imported module_d")
    print(f"Function D result: {module_d.function_d()}")
except Exception as e:
    print(f"❌ Failed to import module_d: {e}")

# Test 5: Test what happens with function calls
print("\n4. Testing function calls across circular imports...")
try:
    # Try to call functions that depend on each other
    result_c = module_c.function_c()
    result_d = module_d.function_d()
    print(f"Function C result: {result_c}")
    print(f"Function D result: {result_d}")
except Exception as e:
    print(f"❌ Error calling functions: {e}")

print("\n🎯 CIRCULAR IMPORT TEST COMPLETE!")

# Cleanup
import os
for file in ["module_a.py", "module_b.py", "module_c.py", "module_d.py"]:
    if os.path.exists(file):
        os.remove(file)
        print(f"Cleaned up {file}")

