import schedule
import threading
import time
from typing import Callable, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from main import PronoteNotifier

logger = logging.getLogger(__name__)


class SchedulerManager:
    def __init__(self, notifier: "PronoteNotifier") -> None:
        self.notifier: "PronoteNotifier" = notifier
        self.scheduler: schedule.Scheduler = schedule.Scheduler()
        self.running: bool = False
        self.scheduler_thread: threading.Thread | None = None
        self._new_grades_callbacks: list[Callable] = []
        self._new_homework_callbacks: list[Callable] = []

    def register_new_grade_callback(self, callback: Callable) -> None:
        """Register a callback to be called when new grades are detected."""
        self._new_grades_callbacks.append(callback)

    def register_new_homework_callback(self, callback: Callable) -> None:
        """Register a callback to be called when new homework is detected."""
        self._new_homework_callbacks.append(callback)

    def _check_new_grades(self) -> None:
        """Check for new grades and trigger callbacks if found."""
        try:
            old_grades = self.notifier.get_grades().copy()
            self.notifier.sync_grades()
            new_grades = self.notifier.get_grades()

            new_grade_ids = {g.id for g in new_grades}
            old_grade_ids = {g.id for g in old_grades}

            newly_added = new_grade_ids - old_grade_ids
            if newly_added:
                new_grade_objects = [g for g in new_grades if g.id in newly_added]
                logger.info(f"Found {len(newly_added)} new grade(s)")
                for callback in self._new_grades_callbacks:
                    try:
                        callback(new_grade_objects)
                    except Exception as e:
                        logger.error(f"Error in grade callback: {e}")
        except Exception as e:
            logger.error(f"Error checking for new grades: {e}")

    def _check_new_homework(self) -> None:
        """Check for new homework and trigger callbacks if found."""
        try:
            old_homework = self.notifier.get_homework().copy()
            self.notifier.sync_homework()
            new_homework = self.notifier.get_homework()

            new_homework_ids = {h.id for h in new_homework}
            old_homework_ids = {h.id for h in old_homework}

            newly_added = new_homework_ids - old_homework_ids
            if newly_added:
                new_homework_objects = [h for h in new_homework if h.id in newly_added]
                logger.info(f"Found {len(newly_added)} new homework item(s)")
                for callback in self._new_homework_callbacks:
                    try:
                        callback(new_homework_objects)
                    except Exception as e:
                        logger.error(f"Error in homework callback: {e}")
        except Exception as e:
            logger.error(f"Error checking for new homework: {e}")

    def schedule_check_grades(self, interval_minutes: int = 30) -> None:
        """Schedule periodic grade checks."""
        self.scheduler.every(interval_minutes).minutes.do(self._check_new_grades)
        logger.info(f"Scheduled grade check every {interval_minutes} minutes")

    def schedule_check_homework(self, interval_minutes: int = 30) -> None:
        """Schedule periodic homework checks."""
        self.scheduler.every(interval_minutes).minutes.do(self._check_new_homework)
        logger.info(f"Scheduled homework check every {interval_minutes} minutes")

    def schedule_check_both(self, interval_minutes: int = 30) -> None:
        """Schedule both grade and homework checks."""
        self.schedule_check_grades(interval_minutes)
        self.schedule_check_homework(interval_minutes)

    def _run_scheduler(self) -> None:
        """Run the scheduler loop."""
        logger.info("Scheduler started")
        while self.running:
            self.scheduler.run_pending()
            time.sleep(1)
        logger.info("Scheduler stopped")

    def start(self) -> None:
        """Start the scheduler in a background thread."""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler, daemon=True
        )
        self.scheduler_thread.start()
        logger.info("Scheduler thread started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if not self.running:
            logger.warning("Scheduler is not running")
            return

        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def clear_schedule(self) -> None:
        """Clear all scheduled jobs."""
        self.scheduler.clear()
        logger.info("Schedule cleared")
