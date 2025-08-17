import yaml, os

def get_task(task_id: str):
    path = os.path.join(os.path.dirname(__file__), "tasks.yaml")
    items = yaml.safe_load(open(path, encoding="utf-8"))
    for it in items:
        if it["id"] == task_id:
            return it
    raise KeyError(task_id)
