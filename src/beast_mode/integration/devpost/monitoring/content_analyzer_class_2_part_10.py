from src.rm_ddd.core.registry import register_module

    def _analyze_media_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze media file for metadata."""
        if not file_path.exists():
            return None
        metadata = {'file_size': file_path.stat().st_size, 'mime_type': mimetypes.guess_type(str(file_path))[0], 'category': self._get_media_category(file_path)}
        try:
            if PIL_AVAILABLE and metadata['category'] == 'image':
                try:
                    with Image.open(file_path) as img:
                        metadata.update({'width': img.width, 'height': img.height, 'format': img.format, 'mode': img.mode})
                except Exception as e:
                    logger.debug(f'Could not analyze image {file_path}: {e}')
            elif metadata['category'] == 'video':
                try:
                    result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', str(file_path)], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        import json
from src.rm_ddd.core.health import ModuleHealth

                        video_info = json.loads(result.stdout)
                        if 'format' in video_info:
                            metadata['duration'] = float(video_info['format'].get('duration', 0))
                        if 'streams' in video_info:
                            for stream in video_info['streams']:
                                if stream.get('codec_type') == 'video':
                                    metadata['width'] = stream.get('width')
                                    metadata['height'] = stream.get('height')
                                    break
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    logger.debug(f'Could not analyze video {file_path}')
        except Exception as e:
            logger.error(f'Error analyzing media file {file_path}: {e}')
        return metadata

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

