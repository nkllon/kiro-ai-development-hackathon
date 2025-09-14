
def _analyze_missing_files(self, failure: Failure) -> Dict[str, Any]:
    """Analyze missing file issues in make context"""
    missing_files = {}
    if 'No such file' in failure.error_message:
        missing_files['has_missing_files'] = True
        if 'No such file or directory:' in failure.error_message:
            missing_files['missing_file'] = failure.error_message.split('No such file or directory:')[1].strip()
    else:
        missing_files['has_missing_files'] = False
    return missing_files
