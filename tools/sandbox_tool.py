import ast
import subprocess
import sys
import tempfile
import os
from utils.logger import get_logger

logger = get_logger("sandbox_tool")

BLOCKED = ["os.system", "subprocess", "shutil.rmtree", "__import__", "eval", "exec", "importlib"]

def is_safe(code: str) -> tuple:
    for keyword in BLOCKED:
        if keyword in code:
            return False, f"Blocked keyword: {keyword}"
    try:
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

def run_code(code: str) -> str:
    safe, reason = is_safe(code)
    if not safe:
        return f"BLOCKED: {reason}"
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp_path = f.name
        result = subprocess.run([sys.executable, tmp_path], capture_output=True, text=True, timeout=15)
        os.unlink(tmp_path)
        return (result.stdout or result.stderr or "No output")[:2000]
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Code took too long"
    except Exception as e:
        return f"ERROR: {str(e)}"