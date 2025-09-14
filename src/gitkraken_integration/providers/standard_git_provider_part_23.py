from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _parse_status_output(self, output: str) -> List[FileStatus]:
        """Parse git status --porcelain output into FileStatus objects"""
        files = []
        for line in output.strip().split('\n'):
            if not line:
                continue
            if len(line) < 3:
                continue
            index_status = line[0]
            working_tree_status = line[1]
            file_path = line[3:]
            if index_status == '?' and working_tree_status == '?':
                status = '??'
                staged = False
            elif index_status != ' ':
                status = index_status
                staged = True
            else:
                status = working_tree_status
                staged = False
            files.append(FileStatus(path=file_path, status=status, staged=staged, working_tree_status=working_tree_status, index_status=index_status))
        return files
