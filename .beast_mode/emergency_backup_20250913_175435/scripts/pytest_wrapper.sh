#!/bin/bash
# pytest wrapper - only allows execution through make

# Check if we're being called by make
check_parent_process() {
	local parent_pid=$(ps -o ppid= -p $$)
	local parent_name=$(ps -o comm= -p "parent_pid")

	# Allow if parent is make
	if [[ ""parent_nam"e" == "make" ]]; then
		return 0
	fi

	# Allow if we're in a make environment
	if [[ -n ""MAKEFLAG"S" || -n ""MAKELEVE"L" ]]; then
		return 0
	fi

	# Block direct execution
	echo "❌ ERROR: pytest can only be executed through make"
	echo "✅ Use: make test"
	echo "📋 Available test targets:"
	echo "   - make test"
	echo "   - make test-all"
	echo "   - make test-python"
	echo "   - make test-model-driven"
	exit 1
}

# Check parent process before executing
check_parent_process

# If we get here, execution is allowed
exec /home/lou/.local/bin/pytest "$@"
