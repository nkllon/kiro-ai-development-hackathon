from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, domain_context: str, external_system_name: str, context_mapping: ContextMapping):
        translator = DictionaryTranslator(context_mapping)
        super().__init__(domain_context, external_system_name, translator)
