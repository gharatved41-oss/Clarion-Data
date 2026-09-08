import os
import difflib
import uuid
import time
import py_compile
from typing import Dict, Any, List, Optional

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKUP_DIR = os.path.join(WORKSPACE_ROOT, ".ai_backups")
CHANGELOG_FILE = os.path.join(WORKSPACE_ROOT, "AI_CHANGELOG.md")

class FileOpsService:
    """Secure, controlled file inspection and editing service with user approval workflow."""
    
    _pending_proposals: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _resolve_safe_path(cls, rel_path: str) -> Optional[str]:
        """Resolves path strictly within WORKSPACE_ROOT and blocks traversal or sensitive files."""
        clean_rel = rel_path.strip().lstrip("/\\")
        abs_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, clean_rel))
        
        # Check boundary
        if not abs_path.startswith(WORKSPACE_ROOT):
            return None
        
        # Block access to environment secrets or git internals
        base_name = os.path.basename(abs_path)
        if base_name in [".env", ".env.local"] or ".git" in abs_path:
            return None

        return abs_path

    @classmethod
    def list_files(cls, subpath: str = "") -> List[Dict[str, Any]]:
        """Lists repository files safely relative to workspace root."""
        target_dir = cls._resolve_safe_path(subpath) if subpath else WORKSPACE_ROOT
        if not target_dir or not os.path.isdir(target_dir):
            return []

        results = []
        ignored = {".git", "__pycache__", ".pytest_cache", ".ai_backups", ".venv", "venv"}

        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in ignored]
            for f in files:
                if f.endswith((".pyc", ".pyo", ".pyd")) or f in [".env"]:
                    continue
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, WORKSPACE_ROOT).replace("\\", "/")
                results.append({
                    "path": rel_path,
                    "name": f,
                    "size": os.path.getsize(full_path),
                    "extension": os.path.splitext(f)[1]
                })

        return sorted(results, key=lambda x: x["path"])

    @classmethod
    def read_file(cls, rel_path: str, max_lines: Optional[int] = None) -> Dict[str, Any]:
        """Reads file content safely with optional line limits."""
        abs_path = cls._resolve_safe_path(rel_path)
        if not abs_path or not os.path.isfile(abs_path):
            return {"error": f"File '{rel_path}' not found or inaccessible."}

        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            
            if max_lines is not None and len(lines) > max_lines:
                content = "".join(lines[:max_lines])
                is_truncated = True
            else:
                content = "".join(lines)
                is_truncated = False

            return {
                "file_path": rel_path,
                "content": content,
                "total_lines": len(lines),
                "is_truncated": is_truncated
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    @classmethod
    def search_files(cls, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """Searches project text files for occurrences of a string."""
        if not query or len(query.strip()) < 2:
            return []

        q = query.lower()
        matches = []
        all_files = cls.list_files()

        for file_info in all_files:
            rel = file_info["path"]
            abs_path = os.path.join(WORKSPACE_ROOT, rel)
            if not os.path.isfile(abs_path):
                continue
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    for idx, line in enumerate(f, start=1):
                        if q in line.lower():
                            matches.append({
                                "file": rel,
                                "line": idx,
                                "content": line.strip()
                            })
                            if len(matches) >= max_results:
                                return matches
            except Exception:
                continue

        return matches

    @classmethod
    def propose_edit(cls, rel_path: str, new_content: str, summary: str) -> Dict[str, Any]:
        """Generates a structured edit proposal and diff without modifying the file."""
        abs_path = cls._resolve_safe_path(rel_path)
        if not abs_path:
            return {"error": f"Target path '{rel_path}' is outside workspace boundary."}

        original_content = ""
        is_new_file = not os.path.exists(abs_path)
        if not is_new_file:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                original_content = f.read()

        # Compute unified diff
        orig_lines = original_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff_lines = list(difflib.unified_diff(
            orig_lines, new_lines,
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}"
        ))
        diff_text = "".join(diff_lines)

        proposal_id = str(uuid.uuid4())[:8]
        cls._pending_proposals[proposal_id] = {
            "proposal_id": proposal_id,
            "file_path": rel_path,
            "abs_path": abs_path,
            "is_new_file": is_new_file,
            "original_content": original_content,
            "new_content": new_content,
            "summary": summary,
            "diff": diff_text or "(No textual differences)",
            "created_at": time.time()
        }

        return {
            "proposal_id": proposal_id,
            "file_path": rel_path,
            "is_new_file": is_new_file,
            "summary": summary,
            "diff": diff_text or "(No textual differences)",
            "status": "pending_user_approval"
        }

    @classmethod
    def apply_edit(cls, proposal_id: str) -> Dict[str, Any]:
        """Applies an approved edit proposal, creating an automatic backup and syntax check."""
        proposal = cls._pending_proposals.get(proposal_id)
        if not proposal:
            return {"error": f"Proposal ID '{proposal_id}' expired or not found."}

        abs_path = proposal["abs_path"]
        rel_path = proposal["file_path"]
        new_content = proposal["new_content"]
        orig_content = proposal["original_content"]

        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_fname = rel_path.replace("/", "_").replace("\\", "_")
        backup_file = os.path.join(BACKUP_DIR, f"{timestamp}_{safe_fname}")

        # 1. Create backup if file exists
        if os.path.exists(abs_path):
            with open(backup_file, "w", encoding="utf-8") as bf:
                bf.write(orig_content)

        # 2. Write new content
        parent_dir = os.path.dirname(abs_path)
        os.makedirs(parent_dir, exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        # 3. Syntax validation for Python files
        if abs_path.endswith(".py"):
            try:
                py_compile.compile(abs_path, doraise=True)
            except Exception as compile_err:
                # Immediate rollback on compilation error
                if os.path.exists(backup_file):
                    with open(abs_path, "w", encoding="utf-8") as f:
                        f.write(orig_content)
                del cls._pending_proposals[proposal_id]
                return {
                    "error": f"Validation failed: Python syntax error in modified code ({str(compile_err)}). Edit was automatically rolled back."
                }

        # 4. Log to AI_CHANGELOG.md
        changelog_entry = f"\n### [{timestamp}] AI Edit applied to `{rel_path}`\n- **Summary**: {proposal['summary']}\n- **Backup**: `{os.path.basename(backup_file)}`\n"
        with open(CHANGELOG_FILE, "a", encoding="utf-8") as cl:
            cl.write(changelog_entry)

        del cls._pending_proposals[proposal_id]

        return {
            "success": True,
            "file_path": rel_path,
            "backup_file": os.path.basename(backup_file),
            "message": f"Successfully applied changes to '{rel_path}' with backup preserved.",
            "status": "applied"
        }

    @classmethod
    def cancel_edit(cls, proposal_id: str) -> Dict[str, Any]:
        """Cancels a pending edit proposal."""
        if proposal_id in cls._pending_proposals:
            del cls._pending_proposals[proposal_id]
            return {"success": True, "message": "Proposal cancelled successfully."}
        return {"error": "Proposal not found or already processed."}

    @classmethod
    def get_changelog(cls) -> str:
        """Returns the AI modification audit changelog."""
        if os.path.exists(CHANGELOG_FILE):
            with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
                return f.read()
        return "No AI file modifications recorded yet."
