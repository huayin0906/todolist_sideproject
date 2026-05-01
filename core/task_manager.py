from core.models import AppSettings, HistoryRecord, Task
from core.storage import save_data

MAX_MISSED_HISTORY = 30


class TaskManager:
    def __init__(self, tasks: list, settings: AppSettings, history: list = None):
        self.tasks: list[Task] = tasks
        self._settings = settings
        self.history: list[HistoryRecord] = history or []

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

    def get(self, task_id: str):
        return next((t for t in self.tasks if t.id == task_id), None)

    # ── reset + history ───────────────────────────────────────────────────────

    def reset_and_record(self, task_id: str, reset_at: str, late_until: str) -> None:
        """Reset a task's completion state and record the cycle result."""
        for task in self.tasks:
            if task.id != task_id:
                continue
            was_done = task.completed

            # Reset the task
            task.completed = False
            task.last_reset = reset_at

            # Store per-task cycle state
            task.last_cycle_done = was_done
            task.late_submitted = False
            task.late_until = late_until if not was_done else ""

            # Append to global missed history
            if not was_done:
                record = HistoryRecord(
                    task_id=task.id,
                    task_title=task.title,
                    reset_at=reset_at,
                    was_done=False,
                    late_submitted=False,
                    late_until=late_until,
                )
                self.history.insert(0, record)
                self.history = self.history[:MAX_MISSED_HISTORY]
            break

        self._save()

    def submit_late(self, task_id: str) -> None:
        """Mark the current missed cycle as late-submitted."""
        for task in self.tasks:
            if task.id == task_id:
                task.late_submitted = True
                break
        for record in self.history:
            if (record.task_id == task_id
                    and not record.was_done
                    and not record.late_submitted):
                record.late_submitted = True
                break
        self._save()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _renumber(self) -> None:
        for i, task in enumerate(self.tasks):
            task.order = i

    def _save(self) -> None:
        save_data(self.tasks, self._settings, self.history)
