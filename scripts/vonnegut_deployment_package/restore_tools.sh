#!/bin/bash
# Restore original tools

echo "🔄 Restoring original tools..."

# Restore pytest
if [[ -f /home/lou/.local/bin/pytest.original ]]; then
	cp /home/lou/.local/bin/pytest.original /home/lou/.local/bin/pytest
	chmod +x /home/lou/.local/bin/pytest
	echo "✅ Restored pytest"
fi

# Remove symbolic links
rm -f /home/lou/.local/bin/flake8
rm -f /home/lou/.local/bin/black
rm -f /home/lou/.local/bin/mypy

echo "✅ Tools restored to original state"
