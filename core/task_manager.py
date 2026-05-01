from core.models import AppSettings, Task
from core.storage import save_data


class TaskManager:
    def __init__(self, tasks: list, settings: AppSettings):
        self.tasks: list[Task] = tasks
        self._settings = settings

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def add(self, task: Task) -> None:
        task.order = len(self.tasks)
        self.tasks.append(task)
        self._save()

    def update(self, task: Task) -> None:
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                break
        self._save()

    def delete(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self._renumber()
        self._save()

    def toggle(self, task_id: str) -> None:
        for task in self.tasks:
            if task.id == task_id:
                task.completed = not task.completed
                break
        self._save()

    def reorder(self, id_sequence: list) -> None:
        by_id = {t.id: t for t in self.tasks}
        self.tasks = [by_id[tid] for tid in id_sequence if tid in by_id]
        self._renumber()
        self._save()

    def reset_task(self, task_id: str, timestamp: str) -> None:
        for task in self.tasks:
            if task.id == task_id:
                task.completed = False
                task.last_reset = timestamp
                break
        self._save()

    def get(self, task_id: str):
        return next((t for t in self.tasks if t.id == task_id), None)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _renumber(self) -> None:
        for i, task in enumerate(self.tasks):
            task.order = i

    def _save(self) -> None:
        save_data(self.tasks, self._settings)
