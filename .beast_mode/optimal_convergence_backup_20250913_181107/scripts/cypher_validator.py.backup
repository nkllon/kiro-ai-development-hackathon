#!/usr/bin/env python3
"""
Cypher Validator - Uses Neo4j Python API to validate Cypher syntax

This script validates Cypher queries using our existing Neo4j database
through the official Python driver instead of subprocess calls.
"""

from pathlib import Path
from typing import Any, Dict, List

from neo4j import GraphDatabase


class CypherValidator:
    """Validates Cypher queries using Neo4j Python API"""

    def __init__(
        self,
        uri: str = "neo4j://localhost:7687",
        username: str = "neo4j",
        password: str = "qwzx8187",
    ):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        """Close the database connection"""
        self.driver.close()

    def validate_query(self, query: str) -> dict[str, Any]:
        """Validate a single Cypher query"""
        try:
            # Clean the query
            clean_query = query.strip()
            if not clean_query.endswith(";"):
                clean_query += ";"

            # Use Neo4j Python API to validate
            with self.driver.session() as session:
                # Try to execute the query (this will catch syntax errors)
                result = session.run(clean_query)
                # Consume the result to ensure it executes
                list(result)

            return {
                "valid": True,
                "query": clean_query,
                "result": "Query executed successfully",
                "errors": [],
            }

        except Exception as e:
            return {"valid": False, "query": query, "result": None, "errors": [str(e)]}

    def validate_file(self, file_path: str) -> dict[str, Any]:
        """Validate all Cypher queries in a file"""
        try:
            with open(file_path) as f:
                content = f.read()

            # Split into individual queries
            queries = self._split_queries(content)

            results = []
            valid_count = 0
            invalid_count = 0

            for i, query in enumerate(queries):
                if query.strip():
                    result = self.validate_query(query)
                    results.append(result)

                    if result["valid"]:
                        valid_count += 1
                    else:
                        invalid_count += 1

            return {
                "file_path": file_path,
                "total_queries": len(queries),
                "valid_queries": valid_count,
                "invalid_queries": invalid_count,
                "results": results,
                "overall_valid": invalid_count == 0,
            }

        except Exception as e:
            return {"file_path": file_path, "error": str(e), "overall_valid": False}

    def _split_queries(self, content: str) -> list[str]:
        """Split content into individual Cypher queries"""
        # Split by complete Cypher statements
        # Each query starts with a comment and ends with a semicolon
        queries = []
        current_query = []
        in_query = False

        for line in content.split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Start of a new query (comment line)
            if line.startswith("-- Query"):
                # If we have a previous query, save it
                if current_query:
                    queries.append("\n".join(current_query).strip())
                    current_query = []

                # Start new query (but don't include the comment)
                in_query = True
                current_query = []
            elif in_query:
                # Continue current query
                current_query.append(line)

                # Check if this line ends the query (contains semicolon)
                if ";" in line:
                    in_query = False

        # Add the last query
        if current_query:
            queries.append("\n".join(current_query).strip())

        return [q for q in queries if q.strip()]

    def fix_cypher_file(
        self, input_file: str, output_file: str = None
    ) -> dict[str, Any]:
        """Fix common Cypher syntax issues in a file"""
        if output_file is None:
            output_file = input_file

        try:
            with open(input_file) as f:
                content = f.read()

            # Fix common issues
            fixed_content = self._fix_cypher_syntax(content)

            with open(output_file, "w") as f:
                f.write(fixed_content)

            return {
                "success": True,
                "input_file": input_file,
                "output_file": output_file,
                "fixes_applied": self._get_fixes_applied(content, fixed_content),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fix_cypher_syntax(self, content: str) -> str:
        """Fix common Cypher syntax issues"""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Skip comment lines
            if line.strip().startswith("--"):
                fixed_lines.append(line)
                continue

            # Skip empty lines
            if not line.strip():
                fixed_lines.append(line)
                continue

            # Fix: Ensure statements end with semicolon
            stripped = line.strip()
            if (
                stripped.startswith("CREATE")
                or stripped.startswith("MATCH")
                or stripped.startswith("RETURN")
                or stripped.startswith("WITH")
                or stripped.startswith("MERGE")
                or stripped.startswith("DELETE")
                or stripped.startswith("SET")
            ):
                if not stripped.endswith(";"):
                    line = line.rstrip() + ";"

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _get_fixes_applied(self, original: str, fixed: str) -> list[str]:
        """Get list of fixes applied"""
        fixes = []

        if original != fixed:
            # Count semicolons added
            original_semicolons = original.count(";")
            fixed_semicolons = fixed.count(";")
            if fixed_semicolons > original_semicolons:
                fixes.append(
                    f"Added {fixed_semicolons - original_semicolons} semicolons"
                )

        return fixes


def main():
    """Main function for Cypher validation"""
    validator = CypherValidator()

    try:
        # Validate our generated Cypher file
        input_file = "neo4j_setup.cypher"

        if Path(input_file).exists():
            print(f"🔍 Validating Cypher file: {input_file}")

            # First, try to fix common syntax issues
            fix_result = validator.fix_cypher_file(input_file, "neo4j_fixed.cypher")

            if fix_result["success"]:
                print(f"✅ Fixed Cypher syntax issues: {fix_result['fixes_applied']}")

                # Now validate the fixed file
                validation_result = validator.validate_file("neo4j_fixed.cypher")

                print(f"📊 Validation Results:")
                print(f"  Total queries: {validation_result['total_queries']}")
                print(f"  Valid queries: {validation_result['valid_queries']}")
                print(f"  Invalid queries: {validation_result['invalid_queries']}")
                print(
                    f"  Overall valid: {
                        '✅' if validation_result['overall_valid'] else '❌'}"
                )

                if not validation_result["overall_valid"]:
                    print("\n❌ Invalid queries found:")
                    for result in validation_result["results"]:
                        if not result["valid"]:
                            print(f"  - {result['errors']}")
            else:
                print(f"❌ Failed to fix Cypher file: {fix_result['error']}")
        else:
            print(f"❌ Cypher file not found: {input_file}")

    finally:
        # Always close the connection
        validator.close()


if __name__ == "__main__":
    main()
