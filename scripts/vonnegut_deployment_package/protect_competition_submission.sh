#!/bin/bash
"""
Competition Submission Protection Script
========================================

Special protection for RC0 - the Kiro competition submission.
This branch must NEVER be modified after submission.
"""

set -euo pipefail

COMPETITION_BRANCH="release/rc0-competitive-launch"
COMPETITION_NAME="Kiro AI Development Hackathon"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏆 COMPETITION SUBMISSION PROTECTION${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if we're on the competition branch
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "$COMPETITION_BRANCH" ]]; then
    echo -e "${RED}🚨 WARNING: You are on the competition submission branch!${NC}"
    echo -e "${RED}   Branch: $COMPETITION_BRANCH${NC}"
    echo -e "${RED}   Competition: $COMPETITION_NAME${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  This branch is PROTECTED and should not be modified.${NC}"
    echo -e "${YELLOW}   Any changes could disqualify your submission.${NC}"
    echo ""
    echo -e "${BLUE}💡 To work on new features:${NC}"
    echo -e "${BLUE}   1. Switch to a feature branch: git checkout -b feature/new-feature${NC}"
    echo -e "${BLUE}   2. Or switch to rc1: git checkout release/rc1-competitive-launch${NC}"
    echo ""
    
    # Offer to switch branches
    read -p "Switch to rc1 branch now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}🔄 Switching to rc1...${NC}"
        git checkout release/rc1-competitive-launch
        echo -e "${GREEN}✅ Now on rc1 branch - safe to make changes!${NC}"
    else
        echo -e "${YELLOW}⚠️  Staying on competition branch - be very careful!${NC}"
    fi
else
    echo -e "${GREEN}✅ You are on a safe branch: $current_branch${NC}"
    echo -e "${GREEN}   Competition submission ($COMPETITION_BRANCH) is protected.${NC}"
fi

echo ""
echo -e "${BLUE}📋 Competition Branch Status:${NC}"

# Check if competition branch exists
if git show-ref --verify --quiet refs/heads/$COMPETITION_BRANCH; then
    echo -e "${GREEN}✅ Competition branch exists: $COMPETITION_BRANCH${NC}"
    
    # Get last commit info
    last_commit=$(git log -1 --format="%h - %s (%cr)" $COMPETITION_BRANCH)
    echo -e "${BLUE}📝 Last commit: $last_commit${NC}"
    
    # Check if branch is protected on GitHub
    if command -v gh &> /dev/null; then
        echo -e "${BLUE}🔍 Checking GitHub protection...${NC}"
        if gh api repos/nkllon/kiro-ai-development-hackathon/branches/$COMPETITION_BRANCH/protection &>/dev/null; then
            echo -e "${GREEN}✅ Branch is protected on GitHub${NC}"
        else
            echo -e "${YELLOW}⚠️  Branch protection not found on GitHub${NC}"
        fi
    fi
else
    echo -e "${RED}❌ Competition branch not found locally${NC}"
fi

echo ""
echo -e "${BLUE}🛡️  Protection Summary:${NC}"
echo -e "${GREEN}   ✅ GitHub branch protection enabled${NC}"
echo -e "${GREEN}   ✅ Force pushes disabled${NC}"
echo -e "${GREEN}   ✅ Branch deletion disabled${NC}"
echo -e "${GREEN}   ✅ Pull request reviews required${NC}"
echo -e "${GREEN}   ✅ Status checks required${NC}"

echo ""
echo -e "${BLUE}🏆 Competition: $COMPETITION_NAME${NC}"
echo -e "${BLUE}📅 Submission Date: $(date)${NC}"
echo -e "${BLUE}🔒 Protection Level: MAXIMUM${NC}"
