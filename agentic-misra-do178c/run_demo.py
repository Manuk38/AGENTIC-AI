from orchestrator.graph import app
from eval.tasks import get_task

def main():
    task = get_task("CRC16")
    result = app.invoke({"nlr": task["nlr"], "constraints": task["constraints"]})
    print("Report:", result.get("report_path"))
    print("Build OK:", result.get("build",{}).get("ok"))

if __name__ == "__main__":
    main()
