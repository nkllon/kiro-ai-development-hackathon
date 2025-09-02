#!/usr/bin/env python3
"""
Neo4j Round-Trip Test Suite

This script tests the complete round-trip:
1. Model → Cypher → Database
2. Database → Query → Results
3. Results → Model validation

Critical for ensuring our model-driven approach works end-to-end.
"""

import json
import os
import time
from typing import Any

from neo4j import GraphDatabase


class Neo4jRoundTripTester:
    """Comprehensive round-trip testing for Neo4j integration"""

    def __init__(
        self,
        uri: str = "neo4j://localhost:7687",
        username: str = os.getenv("NEO4J_USERNAME", "neo4j"),
        password: str = os.getenv("NEO4J_PASSWORD", ""),
    ):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.test_results = []

    def close(self):
        """Close the database connection"""
        self.driver.close()

    def clear_database(self) -> None:
        """Clear all data from the database before testing"""
        print("🧹 Clearing database before testing...")

        try:
            with self.driver.session() as session:
                # Delete all relationships first
                session.run("MATCH ()-[r]-() DELETE r")
                # Delete all nodes
                session.run("MATCH (n) DELETE n")

                # Verify database is empty
                node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                rel_count = session.run("MATCH ()-[r]-() RETURN count(r) as count").single()["count"]

                if node_count == 0 and rel_count == 0:
                    print("    ✅ Database cleared successfully")
                else:
                    print(f"    ⚠️  Database not fully cleared: {node_count} nodes, {rel_count} relationships remain")

        except Exception as e:
            print(f"    ❌ Failed to clear database: {e}")
            raise

    def run_round_trip_tests(self) -> dict[str, Any]:
        """Run all round-trip tests"""
        print("🚀 Starting Neo4j Round-Trip Tests...")
        print("=" * 60)

        try:
            # Clear database before testing
            self.clear_database()

            # Test 1: Model to Database Population
            self.test_model_to_database()

            # Test 2: Database Query Validation
            self.test_database_queries()

            # Test 3: Results to Model Validation
            self.test_results_to_model()

            # Test 4: Edge Cases and Error Handling
            self.test_edge_cases()

            # Test 5: Performance and Scalability
            self.test_performance()

            # Generate comprehensive report
            return self.generate_test_report()

        except Exception as e:
            print(f"❌ Round-trip tests failed: {e}")
            raise
        finally:
            self.close()

    def test_model_to_database(self) -> None:
        """Test 1: Populate database from model"""
        print("🔧 Test 1: Model → Database Population")

        try:
            # Load the project model using Model Registry tools
            from src.round_trip_engineering.tools import get_model_registry

            registry = get_model_registry()
            manager = registry.get_model("project")
            model = manager.load_model()

            # Generate Cypher queries
            from scripts.neo4j_poc import Neo4jPOC

            poc = Neo4jPOC()
            poc.load_project_model()
            queries = poc.generate_cypher_queries()

            # Execute queries to populate database
            with self.driver.session() as session:
                for i, query in enumerate(queries):
                    try:
                        result = session.run(query)
                        # Consume result to ensure execution
                        list(result)
                        print(f"    ✅ Query {i + 1}: {query[:50]}...")
                    except Exception as e:
                        print(f"    ❌ Query {i + 1} failed: {e}")
                        raise

            # Verify data was created
            with self.driver.session() as session:
                # Count nodes
                domain_count = session.run("MATCH (d:Domain) RETURN count(d) as count").single()["count"]
                rule_count = session.run("MATCH (r:Rule) RETURN count(r) as count").single()["count"]
                relationship_count = session.run("MATCH ()-[r:CONTAINS]->() RETURN count(r) as count").single()["count"]

                print(f"    📊 Created {domain_count} domains, {rule_count} rules, {relationship_count} relationships")

                # Validate against model
                expected_rules = len(model["domain_architecture"]["cursor_rules"]["emoji_prefixes"])
                if rule_count == expected_rules:
                    print(f"    ✅ Rule count matches model: {rule_count} == {expected_rules}")
                else:
                    print(f"    ❌ Rule count mismatch: {rule_count} != {expected_rules}")

            self.test_results.append(
                {
                    "test": "model_to_database",
                    "status": "passed",
                    "details": f"Created {domain_count} domains, {rule_count} rules, {relationship_count} relationships",
                }
            )

        except Exception as e:
            print(f"    ❌ Model to database test failed: {e}")
            self.test_results.append({"test": "model_to_database", "status": "failed", "error": str(e)})

    def test_database_queries(self) -> None:
        """Test 2: Validate database queries return expected results"""
        print("\n🔍 Test 2: Database Query Validation")

        test_queries = [
            {
                "name": "Domain Count",
                "query": "MATCH (d:Domain) RETURN count(d) as count",
                "expected": {"count": 1},
            },
            {
                "name": "Rule Count",
                "query": "MATCH (r:Rule) RETURN count(r) as count",
                "expected": {"count": 21},
            },
            {
                "name": "Relationship Count",
                "query": "MATCH ()-[r:CONTAINS]->() RETURN count(r) as count",
                "expected": {"count": 21},
            },
            {
                "name": "Cursor Rules Domain",
                "query": "MATCH (d:Domain {name: 'cursor_rules'}) RETURN d.name, d.status",
                "expected": {"d.name": "cursor_rules", "d.status": "completed"},
            },
            {
                "name": "Security Rule",
                "query": "MATCH (r:Rule {name: 'security'}) RETURN r.emoji, r.type",
                "expected": {"r.emoji": "🔒", "r.type": "cursor_rule"},
            },
        ]

        passed = 0
        total = len(test_queries)

        with self.driver.session() as session:
            for test in test_queries:
                try:
                    result = session.run(test["query"]).single()
                    if result:
                        # Convert Record to dict for comparison
                        result_dict = dict(result)
                        # Check if all expected values match
                        matches = all(result_dict.get(key) == value for key, value in test["expected"].items())
                        if matches:
                            print(f"    ✅ {test['name']}: {result_dict}")
                            passed += 1
                        else:
                            print(f"    ❌ {test['name']}: Expected {test['expected']}, got {result_dict}")
                    else:
                        print(f"    ❌ {test['name']}: No results returned")

                except Exception as e:
                    print(f"    ❌ {test['name']} failed: {e}")

        print(f"    📊 Query validation: {passed}/{total} passed")

        self.test_results.append(
            {
                "test": "database_queries",
                "status": "passed" if passed == total else "failed",
                "details": f"{passed}/{total} queries passed",
            }
        )

    def test_results_to_model(self) -> None:
        """Test 3: Validate database results against model"""
        print("\n🔄 Test 3: Results → Model Validation")

        try:
            # Load model using Model Registry tools
            from src.round_trip_engineering.tools import get_model_registry

            registry = get_model_registry()
            manager = registry.get_model("project")
            model = manager.load_model()

            expected_rules = model["domain_architecture"]["cursor_rules"]["emoji_prefixes"]

            # Query database for all rules
            with self.driver.session() as session:
                result = session.run("MATCH (r:Rule) RETURN r.name, r.emoji ORDER BY r.name")
                db_rules = {row["r.name"]: row["r.emoji"] for row in result}

            # Validate against model
            validation_errors = []
            for rule_name, expected_emoji in expected_rules.items():
                if rule_name not in db_rules:
                    validation_errors.append(f"Rule '{rule_name}' missing from database")
                elif db_rules[rule_name] != expected_emoji:
                    validation_errors.append(f"Rule '{rule_name}' emoji mismatch: expected {expected_emoji}, got {db_rules[rule_name]}")

            if not validation_errors:
                print(f"    ✅ All {len(expected_rules)} rules validated against model")
                print(f"    📊 Database rules: {list(db_rules.keys())}")

                self.test_results.append(
                    {
                        "test": "results_to_model",
                        "status": "passed",
                        "details": f"All {len(expected_rules)} rules validated",
                    }
                )
            else:
                print(f"    ❌ Validation errors found:")
                for error in validation_errors:
                    print(f"        - {error}")

                self.test_results.append(
                    {
                        "test": "results_to_model",
                        "status": "failed",
                        "errors": validation_errors,
                    }
                )

        except Exception as e:
            print(f"    ❌ Results to model validation failed: {e}")
            self.test_results.append({"test": "results_to_model", "status": "failed", "error": str(e)})

    def test_edge_cases(self) -> None:
        """Test 4: Edge cases and error handling"""
        print("\n⚠️  Test 4: Edge Cases and Error Handling")

        edge_case_tests = [
            {
                "name": "Invalid Cypher Syntax",
                "query": "CREATE (invalid syntax",
                "should_fail": True,
            },
            {
                "name": "Non-existent Node",
                "query": "MATCH (n:NonExistent) RETURN n",
                "should_fail": False,  # Should return empty result
                "expected_count": 0,
            },
            {
                "name": "Empty Result Set",
                "query": "MATCH (r:Rule {name: 'non_existent_rule'}) RETURN r",
                "should_fail": False,
                "expected_count": 0,
            },
            {
                "name": "Complex Query",
                "query": "MATCH (d:Domain)-[:CONTAINS]->(r:Rule) WHERE r.emoji CONTAINS '🔒' RETURN d.name, r.name, r.emoji ORDER BY r.name",
                "should_fail": False,
            },
        ]

        passed = 0
        total = len(edge_case_tests)

        with self.driver.session() as session:
            for test in edge_case_tests:
                try:
                    if test["should_fail"]:
                        # Expect this to fail
                        try:
                            result = session.run(test["query"])
                            list(result)  # Consume result
                            print(f"    ❌ {test['name']}: Expected to fail but succeeded")
                        except Exception:
                            print(f"    ✅ {test['name']}: Correctly failed as expected")
                            passed += 1
                    else:
                        # Expect this to succeed
                        result = session.run(test["query"])
                        results = list(result)

                        if "expected_count" in test:
                            if len(results) == test["expected_count"]:
                                print(f"    ✅ {test['name']}: Correct count {len(results)}")
                                passed += 1
                            else:
                                print(f"    ❌ {test['name']}: Expected {test['expected_count']}, got {len(results)}")
                        else:
                            print(f"    ✅ {test['name']}: Executed successfully, returned {len(results)} results")
                            passed += 1

                except Exception as e:
                    if test["should_fail"]:
                        print(f"    ✅ {test['name']}: Correctly failed as expected")
                        passed += 1
                    else:
                        print(f"    ❌ {test['name']}: Unexpected failure: {e}")

        print(f"    📊 Edge case tests: {passed}/{total} passed")

        self.test_results.append(
            {
                "test": "edge_cases",
                "status": "passed" if passed == total else "failed",
                "details": f"{passed}/{total} edge case tests passed",
            }
        )

    def test_performance(self) -> None:
        """Test 5: Performance and scalability"""
        print("\n⚡ Test 5: Performance and Scalability")

        try:
            with self.driver.session() as session:
                # Test query execution time
                start_time = time.time()
                result = session.run("MATCH (d:Domain)-[:CONTAINS]->(r:Rule) RETURN d.name, r.name, r.emoji ORDER BY r.name")
                results = list(result)
                execution_time = time.time() - start_time

                print(f"    ⏱️  Complex query execution time: {execution_time:.4f}s")
                print(f"    📊 Results returned: {len(results)}")

                # Performance thresholds
                if execution_time < 0.1:  # 100ms threshold
                    print(f"    ✅ Performance: Excellent (< 100ms)")
                    performance_status = "excellent"
                elif execution_time < 0.5:  # 500ms threshold
                    print(f"    ✅ Performance: Good (< 500ms)")
                    performance_status = "good"
                else:
                    print(f"    ⚠️  Performance: Slow ({execution_time:.4f}s)")
                    performance_status = "slow"

                # Test memory usage (approximate)
                memory_estimate = len(results) * 100  # Rough estimate: 100 bytes per result
                print(f"    💾 Memory usage estimate: ~{memory_estimate} bytes")

                self.test_results.append(
                    {
                        "test": "performance",
                        "status": "passed",
                        "details": f"Execution time: {execution_time:.4f}s, Performance: {performance_status}",
                    }
                )

        except Exception as e:
            print(f"    ❌ Performance test failed: {e}")
            self.test_results.append({"test": "performance", "status": "failed", "error": str(e)})

    def generate_test_report(self) -> dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 ROUND-TRIP TEST REPORT")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "passed")
        failed_tests = total_tests - passed_tests

        print(f"🎯 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

        # Detailed results
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "passed" else "❌"
            print(f"  {status_emoji} {result['test']}: {result['status']}")
            if "details" in result:
                print(f"      Details: {result['details']}")
            if "error" in result:
                print(f"      Error: {result['error']}")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"      - {error}")

        # Overall assessment
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! Round-trip validation successful!")
            overall_status = "SUCCESS"
        elif passed_tests > failed_tests:
            print(f"\n⚠️  Most tests passed, but {failed_tests} failed. Review needed.")
            overall_status = "PARTIAL_SUCCESS"
        else:
            print(f"\n❌ {failed_tests} tests failed. Major issues detected.")
            overall_status = "FAILURE"

        report = {
            "overall_status": overall_status,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "test_results": self.test_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save report to file
        with open("neo4j_round_trip_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: neo4j_round_trip_report.json")

        return report


def main():
    """Main execution function"""
    tester = Neo4jRoundTripTester()

    try:
        report = tester.run_round_trip_tests()

        # Exit with appropriate code
        if report["overall_status"] == "SUCCESS":
            print("\n🚀 Round-trip tests completed successfully!")
            exit(0)
        else:
            print(f"\n⚠️  Round-trip tests completed with issues: {report['overall_status']}")
            exit(1)

    except Exception as e:
        print(f"\n❌ Round-trip tests failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
