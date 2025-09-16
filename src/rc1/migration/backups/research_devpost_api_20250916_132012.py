#!/usr/bin/env python3
"""
Research Devpost API Documentation and Submission Process

Let's find the legitimate, official way to interact with Devpost.
"""

import requests
import json
from pathlib import Path


def research_devpost_api():
    """Research official Devpost API documentation"""

    print("🔍 Researching Official Devpost API...")

    # Common API documentation endpoints to check
    api_endpoints_to_check = [
        "https://devpost.com/api",
        "https://api.devpost.com",
        "https://devpost.com/api/v1",
        "https://devpost.com/developers",
        "https://help.devpost.com/hc/en-us/articles/360021749312-Devpost-API",
        "https://devpost.com/api-docs",
        "https://docs.devpost.com",
    ]

    print("\n📋 Checking common API documentation URLs:")

    for url in api_endpoints_to_check:
        try:
            print(f"\n🌐 Checking: {url}")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"✅ Found: {url} (Status: {response.status_code})")

                # Check if it looks like API documentation
                content = response.text.lower()
                api_indicators = [
                    "api",
                    "endpoint",
                    "authentication",
                    "token",
                    "json",
                    "rest",
                ]

                found_indicators = [
                    indicator for indicator in api_indicators if indicator in content
                ]
                if found_indicators:
                    print(f"   📚 API indicators found: {', '.join(found_indicators)}")

                    # Save the content for analysis
                    filename = f"devpost_api_research_{url.replace('https://', '').replace('/', '_')}.html"
                    Path(filename).write_text(response.text)
                    print(f"   💾 Saved content to: {filename}")
                else:
                    print(f"   ⚠️  No clear API documentation indicators")

            else:
                print(f"❌ Not found: {url} (Status: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error accessing {url}: {e}")

    # Check robots.txt for API hints
    print(f"\n🤖 Checking robots.txt for API hints:")
    try:
        robots_response = requests.get("https://devpost.com/robots.txt", timeout=10)
        if robots_response.status_code == 200:
            robots_content = robots_response.text
            print("✅ Found robots.txt")

            # Look for API-related paths
            api_paths = [
                line
                for line in robots_content.split("\n")
                if "api" in line.lower() or "developer" in line.lower()
            ]

            if api_paths:
                print("   📋 API-related paths found:")
                for path in api_paths:
                    print(f"      {path}")
            else:
                print("   ⚠️  No API paths found in robots.txt")

            Path("devpost_robots.txt").write_text(robots_content)
            print("   💾 Saved robots.txt for analysis")
        else:
            print(
                f"❌ Could not access robots.txt (Status: {robots_response.status_code})"
            )

    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing robots.txt: {e}")

    # Check for GraphQL endpoint (common for modern APIs)
    print(f"\n🔍 Checking for GraphQL endpoint:")
    graphql_endpoints = [
        "https://devpost.com/graphql",
        "https://api.devpost.com/graphql",
        "https://devpost.com/api/graphql",
    ]

    for endpoint in graphql_endpoints:
        try:
            # Try a simple introspection query
            graphql_query = {"query": "{ __schema { types { name } } }"}

            response = requests.post(endpoint, json=graphql_query, timeout=10)

            if response.status_code == 200:
                print(f"✅ GraphQL endpoint found: {endpoint}")

                try:
                    data = response.json()
                    if "data" in data:
                        print("   📊 GraphQL schema accessible")
                        Path(f"devpost_graphql_schema.json").write_text(
                            json.dumps(data, indent=2)
                        )
                        print("   💾 Saved schema to devpost_graphql_schema.json")
                except:
                    print("   ⚠️  Response not valid JSON")

            else:
                print(f"❌ No GraphQL at {endpoint} (Status: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking GraphQL {endpoint}: {e}")


def research_hackathon_submission_process():
    """Research how hackathon submissions actually work on Devpost"""

    print(f"\n\n🎯 Researching Hackathon Submission Process...")

    # Check Devpost help documentation
    help_urls = [
        "https://help.devpost.com/hc/en-us/categories/360002113231-For-Participants",
        "https://help.devpost.com/hc/en-us/articles/360021749312-Devpost-API",
        "https://help.devpost.com/hc/en-us/articles/360021749292-How-do-I-submit-to-a-hackathon-",
        "https://help.devpost.com/hc/en-us/sections/360003543571-Submitting-Projects",
    ]

    for url in help_urls:
        try:
            print(f"\n📖 Checking help documentation: {url}")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"✅ Found documentation: {response.status_code}")

                # Save for analysis
                filename = f"devpost_help_{url.split('/')[-1]}.html"
                Path(filename).write_text(response.text)
                print(f"   💾 Saved to: {filename}")

                # Look for key submission terms
                content = response.text.lower()
                submission_terms = [
                    "submit",
                    "api",
                    "token",
                    "authentication",
                    "project",
                    "hackathon",
                ]
                found_terms = [term for term in submission_terms if term in content]

                if found_terms:
                    print(f"   🔍 Key terms found: {', '.join(found_terms)}")

            else:
                print(f"❌ Documentation not accessible: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error accessing documentation: {e}")


def check_kiro_hackathon_specifics():
    """Check if there's specific information about the Kiro hackathon"""

    print(f"\n\n🎯 Researching Kiro-Specific Hackathon Information...")

    # Search for Kiro hackathon on Devpost
    search_urls = [
        "https://devpost.com/hackathons?search=kiro",
        "https://devpost.com/hackathons?search=kiro+ai",
        "https://devpost.com/hackathons?search=code+with+kiro",
    ]

    for url in search_urls:
        try:
            print(f"\n🔍 Searching: {url}")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"✅ Search results found")

                # Save search results
                search_term = url.split("=")[-1].replace("+", "_")
                filename = f"devpost_search_{search_term}.html"
                Path(filename).write_text(response.text)
                print(f"   💾 Saved search results to: {filename}")

                # Look for hackathon indicators
                content = response.text.lower()
                if "kiro" in content:
                    print("   🎯 Kiro-related content found!")
                else:
                    print("   ⚠️  No Kiro-related content in search results")

            else:
                print(f"❌ Search failed: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Search error: {e}")


def main():
    """Main research function"""
    print("🔬 DEVPOST API RESEARCH")
    print("=" * 50)
    print("Goal: Find legitimate, official ways to interact with Devpost")
    print("Focus: API documentation, submission process, authentication")

    research_devpost_api()
    research_hackathon_submission_process()
    check_kiro_hackathon_specifics()

    print(f"\n\n📋 RESEARCH SUMMARY")
    print("=" * 50)
    print("✅ Checked official API documentation endpoints")
    print("✅ Analyzed robots.txt for API hints")
    print("✅ Tested GraphQL endpoints")
    print("✅ Reviewed help documentation")
    print("✅ Searched for Kiro hackathon specifics")

    print(f"\n💡 Next Steps:")
    print("1. Review saved HTML files for API documentation")
    print("2. Look for authentication methods (OAuth, API keys)")
    print("3. Find official submission endpoints")
    print("4. Identify required project metadata")
    print("5. Understand hackathon registration process")


if __name__ == "__main__":
    main()
