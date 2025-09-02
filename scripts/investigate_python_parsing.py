#!/usr/bin/env python3
"""
Investigate Python Parsing

Purpose: Understand how Python actually parses broken f-strings
"""

import ast
import io
import sys
import tokenize


def investigate_broken_fstring():
    """Investigate how Python handles broken f-strings"""

    print("🔍 Investigating Python F-String Parsing")
    print("=" * 50)

    # The problematic f-string
    broken_code = 'print(f"Count: {len(\\\n    data)}")'

    print(f"Broken code: {repr(broken_code)}")
    print(f"Length: {len(broken_code)}")
    print(f"Contains backslash: {'\\' in broken_code}")
    print(f"Contains newline: {'\\n' in broken_code}")

    # Let's see what Python's tokenizer sees
    print("\n🧪 Python Tokenizer Analysis:")
    try:
        tokens = list(tokenize.tokenize(io.BytesIO(broken_code.encode("utf-8")).readline))
        for token in tokens:
            print(f"  {token.type}: {repr(token.string)} (line {token.start[0]}, col {token.start[1]})")
    except Exception as e:
        print(f"  Tokenizer error: {e}")

    # Let's see what AST parser sees
    print("\n🧪 AST Parser Analysis:")
    try:
        tree = ast.parse(broken_code)
        print(f"  AST parse successful: {type(tree)}")
        print(f"  AST content: {ast.dump(tree, indent=2)}")
    except SyntaxError as e:
        print(f"  AST parse error: {e}")
        print(f"  Error type: {type(e)}")
        print(f"  Error line: {getattr(e, 'lineno', 'N/A')}")
        print(f"  Error offset: {getattr(e, 'offset', 'N/A')}")
        print(f"  Error text: {getattr(e, 'text', 'N/A')}")

    # Let's try to understand what's happening with the backslash
    print("\n🧪 Backslash Analysis:")

    # What if we look at the raw bytes?
    print(f"  Raw bytes: {broken_code.encode('utf-8')}")

    # What if we look at the actual characters?
    for i, char in enumerate(broken_code):
        if char in ["\\", "\n", "{", "}"]:
            print(f"  Char {i}: {repr(char)} (ord: {ord(char)})")

    # Let's try different variations
    print("\n🧪 Testing Variations:")

    variations = [
        'print(f"Count: {len(\\\n    data)}")',  # Original
        'print(f"Count: {len(\\\n    data)}")',  # Same but different
        'print(f"Count: {len(\\\n    data)}")',  # Another variation
    ]

    for i, var in enumerate(variations):
        print(f"\nVariation {i}:")
        print(f"  Code: {repr(var)}")
        try:
            ast.parse(var)
            print("  ✅ Parses successfully")
        except SyntaxError as e:
            print(f"  ❌ Parse error: {e}")
            print(f"  Error type: {type(e).__name__}")

    # Let's see what happens if we try to compile it
    print("\n🧪 Compilation Test:")
    try:
        compiled = compile(broken_code, "<string>", "exec")
        print(f"  Compilation successful: {type(compiled)}")
    except SyntaxError as e:
        print(f"  Compilation error: {e}")
    except Exception as e:
        print(f"  Other error: {e}")


def investigate_flake8_detection():
    """Investigate how flake8 might detect these issues"""

    print("\n🔍 Investigating Flake8 Detection")
    print("=" * 50)

    # Flake8 uses pycodestyle (formerly pep8) and pyflakes
    # Let's see what pyflakes would do
    print("Flake8 uses pyflakes for syntax checking...")

    # Let's try to understand the error message
    error_msg = "f-string expression part cannot include a backslash"
    print(f"Error message: {error_msg}")

    # This suggests that Python's parser IS detecting this
    # But maybe it's a different stage of parsing?

    print("\nThe error message suggests Python DOES detect this!")
    print("Maybe it's during tokenization, not AST parsing?")


def investigate_python_parser_stages():
    """Investigate different stages of Python parsing"""

    print("\n🔍 Investigating Python Parser Stages")
    print("=" * 50)

    broken_code = 'print(f"Count: {len(\\\n    data)}")'

    print("Python parsing has multiple stages:")
    print("1. Lexical analysis (tokenization)")
    print("2. Parsing (AST creation)")
    print("3. Compilation (bytecode generation)")

    print(f"\nTesting with: {repr(broken_code)}")

    # Stage 1: Tokenization
    print("\nStage 1: Tokenization")
    try:
        tokens = list(tokenize.tokenize(io.BytesIO(broken_code.encode("utf-8")).readline))
        print("  ✅ Tokenization successful")
        print(f"  Number of tokens: {len(tokens)}")

        # Look for f-string tokens
        fstring_tokens = [t for t in tokens if t.type == tokenize.STRING and t.string.startswith("f")]
        print(f"  F-string tokens: {len(fstring_tokens)}")
        for t in fstring_tokens:
            print(f"    {repr(t.string)}")

    except Exception as e:
        print(f"  ❌ Tokenization failed: {e}")

    # Stage 2: AST Parsing
    print("\nStage 2: AST Parsing")
    try:
        ast.parse(broken_code)
        print("  ✅ AST parsing successful")
    except SyntaxError as e:
        print(f"  ❌ AST parsing failed: {e}")
        print(f"  This suggests the error is caught during AST parsing")

    # Stage 3: Compilation
    print("\nStage 3: Compilation")
    try:
        compile(broken_code, "<string>", "exec")
        print("  ✅ Compilation successful")
    except SyntaxError as e:
        print(f"  ❌ Compilation failed: {e}")
        print(f"  This suggests the error is caught during compilation")


def main():
    """Main entry point"""
    investigate_broken_fstring()
    investigate_flake8_detection()
    investigate_python_parser_stages()


if __name__ == "__main__":
    main()
