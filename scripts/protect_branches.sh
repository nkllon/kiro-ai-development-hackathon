#!/bin/bash
"""
Branch Protection Script
========================

Prevents accidental changes to protected branches.
"""

set -euo pipefail

# Protected branches (read-only)
PROTECTED_BRANCHES=(
    "master"
    "release/rc0-competitive-launch"
    "release/rc1-competitive-launch"
)

# Current branch
CURRENT_BRANCH=$(git branch --show-current)

# Check if current branch is protected
is_protected() {
    local branch="$1"
    for protected in "${PROTECTED_BRANCHES[@]}"; do
        if [[ "$branch" == "$protected" ]]; then
            return 0
        fi
    done
    return 1
}

# Protection functions
protect_branch() {
    local branch="$1"
    echo "🔒 Protecting branch: $branch"
    
    # Create a pre-commit hook to prevent direct commits
    local hook_file=".git/hooks/pre-commit"
    cat > "$hook_file" << EOF
#!/bin/bash
# Auto-generated branch protection hook

CURRENT_BRANCH=\$(git branch --show-current)

case "\$CURRENT_BRANCH" in
    master|release/rc0-competitive-launch|release/rc1-competitive-launch)
        echo "🚨 ERROR: Direct commits to protected branch '\$CURRENT_BRANCH' are not allowed!"
        echo "💡 Use a feature branch and create a pull request instead."
        echo "🔓 To override (use with caution): git commit --no-verify"
        exit 1
        ;;
esac
EOF
    chmod +x "$hook_file"
}

# Unprotect branch
unprotect_branch() {
    local branch="$1"
    echo "🔓 Unprotecting branch: $branch"
    # Remove the hook
    rm -f ".git/hooks/pre-commit"
}

# Main function
main() {
    case "${1:-help}" in
        "protect")
            protect_branch "${2:-$CURRENT_BRANCH}"
            ;;
        "unprotect")
            unprotect_branch "${2:-$CURRENT_BRANCH}"
            ;;
        "status")
            echo "📊 Branch Protection Status:"
            echo "Current branch: $CURRENT_BRANCH"
            if is_protected "$CURRENT_BRANCH"; then
                echo "Status: 🔒 PROTECTED"
            else
                echo "Status: 🔓 UNPROTECTED"
            fi
            echo ""
            echo "Protected branches:"
            for branch in "${PROTECTED_BRANCHES[@]}"; do
                echo "  - $branch"
            done
            ;;
        "help"|*)
            echo "🔒 Branch Protection Script"
            echo "Usage: $0 [protect|unprotect|status|help] [branch-name]"
            echo ""
            echo "Commands:"
            echo "  protect [branch]  - Protect a branch from direct commits"
            echo "  unprotect [branch]- Remove protection from a branch"
            echo "  status           - Show protection status"
            echo "  help             - Show this help message"
            echo ""
            echo "Protected branches: ${PROTECTED_BRANCHES[*]}"
            ;;
    esac
}

main "$@"
