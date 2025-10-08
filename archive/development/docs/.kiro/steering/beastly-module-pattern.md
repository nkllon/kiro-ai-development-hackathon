# The Beastly Module Pattern 🐺

## Mnemonic: "Beastly Module"
When you need systematic observability, health monitoring, and Prometheus integration, inherit from the **Beastly Module**.

## The One True Import
```python
# ✅ ALWAYS use this import path:
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

# 🐺 Mnemonic: "Beastly Module" = ReflectiveModule from unified core
class YourAwesomeClass(ReflectiveModule):
    """Your class now has beastly powers! 🐺"""
    pass
```

## What You Get (The Beastly Powers)
When you inherit from the Beastly Module, you automatically get:
- 📊 **Prometheus metrics** - automatic registration
- 🏥 **Health endpoints** - `/health`, `/ready`, `/metrics`
- 📈 **Performance tracing** - operation timing
- 🔄 **Graceful degradation** - systematic failure handling
- 📝 **Structured logging** - with correlation IDs
- 🎯 **Error handling** - consistent across all components

## Wrong Imports (Don't Use These)
```python
# ❌ DEPRECATED - old path
from ..core import ReflectiveModule

# ❌ WRONG - beast mode wrapper (just re-exports)
from src.beast_mode.core.reflective_module import ReflectiveModule

# ❌ INCONSISTENT - various other paths
from beast_mode.observatory.core import ReflectiveModule
```

## Memory Aid
**"When you need beastly powers, import from the unified core!"**

- **Beastly** = ReflectiveModule (systematic observability)
- **Unified** = src.rm_ddd.core.unified_reflective_module
- **Core** = The canonical source of truth

## Example Usage
```python
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

class WebSocketManager(ReflectiveModule):
    """WebSocket manager with beastly observability powers! 🐺"""
    
    def __init__(self):
        super().__init__()
        # Your class now automatically:
        # - Registers Prometheus metrics
        # - Provides health endpoints
        # - Traces performance
        # - Handles errors systematically
```

## Why This Works
- **Memorable**: "Beastly Module" sticks in your brain
- **Clear**: One import path, no confusion
- **Systematic**: All components get consistent observability
- **Debuggable**: You know exactly what powers you're getting

## For AI Workers
When building Beast Mode components, always ask:
**"Does this need beastly powers?"**

If yes → inherit from the Beastly Module using the unified import.
If no → use a regular Python class.

---
*Remember: Beastly Module = systematic observability superpowers! 🐺*