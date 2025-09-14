from src.rm_ddd.core.health import ModuleHealth

    def __init__(self):
        self.formats = {'json': self.output_json, 'text': self.output_text, 'table': self.output_table}
