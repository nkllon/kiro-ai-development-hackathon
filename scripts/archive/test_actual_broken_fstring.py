#!/usr/bin/env python3
"""
Test Actual Broken F-String

Purpose: Test the exact f-string that was causing the error
"""

import ast


def test_actual_broken_fstring():
    """Test the actual broken f-string from the Ghostbusters code"""

    print("🧪 Testing Actual Broken F-String from Ghostbusters")
    print("=" * 60)

    # This is the exact f-string that was causing the error
    broken_fstring = 'f"Widespread import organization issues: {len( \\\n    import_errors)}"'

    print(f"Broken f-string: {repr(broken_fstring)}")
    print(f"Length: {len(broken_fstring)}")
    backslash_check = '\\' in broken_fstring
    newline_check = '\\n' in broken_fstring
    print(f"Contains backslash: {backslash_check}")
    print(f"Contains newline: {newline_check}")

    # Let's see what happens when we try to parse it
    print("\n🧪 Testing AST Parsing:")
    try:
        tree = ast.parse(broken_fstring)
        print("  ✅ AST parse successful!")
        print(f"  AST type: {type(tree)}")
    except SyntaxError as e:
        print(f"  ❌ AST parse failed: {e}")
        print(f"  Error type: {type(e)}")
        print(f"  Error line: {getattr(e, 'lineno', 'N/A')}")
        print(f"  Error offset: {getattr(e, 'offset', 'N/A')}")

    # Let's try to parse it as part of a statement
    print("\n🧪 Testing as Statement:")
    statement = f"print({broken_fstring})"
    print(f"Statement: {repr(statement)}")

    try:
        tree = ast.parse(statement)
        print("  ✅ Statement parse successful!")
    except SyntaxError as e:
        print(f"  ❌ Statement parse failed: {e}")

    # Let's try to compile it
    print("\n🧪 Testing Compilation:")
    try:
        compile(statement, "<string>", "exec")
        print("  ✅ Compilation successful!")
    except SyntaxError as e:
        print(f"  ❌ Compilation failed: {e}")

    # Let's see what the actual error was in the original code
    print("\n🔍 Original Error Analysis:")
    print("The error was: 'f-string expression part cannot include a backslash'")
    print("This suggests Python DOES detect this during some parsing stage")

    # Maybe it's a different Python version or parser?
    print(f"\nPython version: {ast.__version__ if hasattr(ast, '__version__') else 'Unknown'}")

    # Let's try to understand why this specific case fails
    print("\n🧪 Why This Case Fails:")
    print("1. The backslash is inside the f-string expression: {len( \\\\")
    print("2. Python's f-string parser doesn't allow backslashes in expressions")
    print("3. But our test case might be different...")

    # Let's check if there's a difference in how we're testing
    print("\n🧪 Testing with Different Approaches:")

    # Approach 1: Direct f-string
    test1 = 'f"Count: {len( \\\n    data)}"'
    print(f"Test 1 (direct): {repr(test1)}")
    try:
        ast.parse(test1)
        print("  ✅ Direct f-string parses")
    except SyntaxError as e:
        print(f"  ❌ Direct f-string fails: {e}")

    # Approach 2: As part of a statement
    test2 = f"print({test1})"
    print(f"Test 2 (statement): {repr(test2)}")
    try:
        ast.parse(test2)
        print("  ✅ Statement parses")
    except SyntaxError as e:
        print(f"  ❌ Statement fails: {e}")

    # Approach 3: As part of a module
    test3 = f"x = {test1}"
    print(f"Test 3 (module): {repr(test3)}")
    try:
        ast.parse(test3)
        print("  ✅ Module parses")
    except SyntaxError as e:
        print(f"  ❌ Module fails: {e}")


def main():
    """Main entry point"""
    test_actual_broken_fstring()


if __name__ == "__main__":
    main()
