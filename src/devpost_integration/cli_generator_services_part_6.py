
    def __init__(self):
        self.formats = {'json': self.process_json_input, 'text': self.process_text_input, 'binary': self.process_binary_input}
