#!/bin/bash
# mypy wrapper - only allows execution through make

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
	echo "❌ ERROR: mypy can only be executed through make"
	echo "✅ Use: make mypy"
	echo "📋 Available targets:"
	echo "   - make mypy"
	echo "   - make mypy-all"
	echo "   - make mypy-python"
	exit 1
}

check_parent_process
exec /home/lou/.local/bin/mypy.original "$@"
