
def _analyze_import_issues(self, failure: Failure) -> Dict[str, Any]:
    """Analyze import-related issues"""
    import_analysis = {}
    if 'ImportError' in failure.error_message or 'ModuleNotFoundError' in failure.error_message:
        import_analysis['has_import_error'] = True
        if 'No module named' in failure.error_message:
            import_analysis['missing_module'] = failure.error_message.split('No module named')[1].strip().strip('\'"')
        import_analysis['relative_import_issue'] = 'relative import' in failure.error_message.lower()
    else:
        import_analysis['has_import_error'] = False
    return import_analysis
