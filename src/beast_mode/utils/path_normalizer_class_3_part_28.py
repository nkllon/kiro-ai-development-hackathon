from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        register_module('PathValidator', self)