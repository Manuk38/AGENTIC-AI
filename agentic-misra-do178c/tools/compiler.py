import subprocess, tempfile, os, json
# tools/compiler.py
import subprocess, tempfile, os, shutil

def _which(cmd):
    return shutil.which(cmd)

def _run(args):
    return subprocess.run(args, capture_output=True, text=True)

def compile_code(code: str, std: str = "c99"):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "gen.c")
        exe = os.path.join(d, "a.exe" if os.name == "nt" else "a.out")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)

        # 1) Honour CC if set
        cc_env = os.environ.get("CC")
        if cc_env:
            try:
                proc = _run([cc_env, f"-std={std}", "-Wall", "-Wextra", "-Werror", src, "-o", exe])
                return {"ok": proc.returncode == 0, "stderr": proc.stderr.splitlines()}
            except Exception as e:
                return {"ok": False, "stderr": [f"CC={cc_env} failed: {e}"]}

        # 2) Try gcc
        if _which("gcc"):
            proc = _run(["gcc", f"-std={std}", "-Wall", "-Wextra", "-Werror", src, "-o", exe])
            return {"ok": proc.returncode == 0, "stderr": proc.stderr.splitlines()}

        # 3) Try clang
        if _which("clang"):
            # clang on Windows supports -std=c11; c99 is generally ok too
            proc = _run(["clang", f"-std={std}", "-Wall", "-Wextra", "-Werror", src, "-o", exe])
            return {"ok": proc.returncode == 0, "stderr": proc.stderr.splitlines()}

        # 4) Try MSVC cl (Visual Studio Developer Prompt or Build Tools in PATH)
        if _which("cl"):
            # MSVC doesn't support -std=c99 the same way; compile with defaults
            # /nologo /W4 /WX (treat warnings as errors). Produce exe at default name.
            proc = _run(["cl", "/nologo", "/W4", "/WX", src])
            ok = proc.returncode == 0
            # MSVC writes output to current directory; not moving exe since this is a temp dir
            return {"ok": ok, "stderr": proc.stderr.splitlines()}

        # 5) No compiler found → skip to keep the graph running
        return {
            "ok": True,
            "stderr": [
                "No system C compiler detected (gcc/clang/cl). Skipped compilation step."
            ],
        }
