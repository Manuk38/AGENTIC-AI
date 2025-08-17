import yaml

def judge_final(code, findings, build, coverage, constitution_path, trace):
    c = yaml.safe_load(open(constitution_path, encoding="utf-8"))
    banned = set(c["misra"]["banned_constructs"])
    # quick scan
    if "goto" in code:
        return {"accept": False, "reason": "goto present"}
    if not build.get("ok"):
        return {"accept": False, "reason": "compile failed"}
    return {"accept": True, "reason": "basic checks pass"}
