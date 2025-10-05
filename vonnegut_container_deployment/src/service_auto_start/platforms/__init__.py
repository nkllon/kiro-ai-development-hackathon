"""Platform-specific service auto-start adapters."""

# Platform adapters will be imported as needed to avoid import errors
# on platforms where they're not supported

__all__ = [
    "MacOSLaunchAgentAdapter",
    "LinuxSystemdAdapter", 
    "DockerComposeAdapter"
]