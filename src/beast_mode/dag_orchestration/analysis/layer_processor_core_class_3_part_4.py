from src.rm_ddd.core.registry import register_module

def __init__(self) -> Any:
    self.parallel_threshold = 2
    self.bottleneck_threshold = 0.3

        register_module(self.__class__.__name__, self)