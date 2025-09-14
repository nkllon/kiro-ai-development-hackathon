from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def file_progress(percent):
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    if progress_callback:
        overall_progress = (i * 100 + percent) / len(media_files)
        progress_callback(int(overall_progress))
