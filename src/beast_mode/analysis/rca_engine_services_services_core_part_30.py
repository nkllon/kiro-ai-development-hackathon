
def _get_make_subcategory(self, failure: Failure) -> str:
    """Get make failure subcategory"""
    if 'No rule to make target' in failure.error_message:
        return 'missing_target'
    elif 'missing separator' in failure.error_message:
        return 'syntax_error'
    elif 'No such file' in failure.error_message:
        return 'missing_file'
    else:
        return 'general_make_error'
