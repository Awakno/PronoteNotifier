"""
Pronote Notifier - Bot de monitoring continu
Lancer avec: python main.py
"""

import pronotepy
from core.client import Client
from memory.grade import GradeManager
from memory.homework import HomeworkManager
from cron import SchedulerManager
from telegram_notifier import TelegramNotifier
import logging
import time
import os
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PronoteNotifier:
    """Client Pronote avec notifications automatiques."""

    def __init__(self, url: str, username: str, password: str) -> None:
        self.client: Client = Client(url, username, password)
        self.grade_manager: GradeManager = GradeManager(self.client.client)
        self.homework_manager: HomeworkManager = HomeworkManager(self.client.client)
        self.scheduler: SchedulerManager = SchedulerManager(self)

    def logout(self) -> bool:
        return self.client.logout()

    @property
    def is_connected(self) -> bool:
        return self.client.is_connected()

    def sync_grades(self) -> None:
        self.grade_manager.update_grades()

    def sync_homework(self) -> None:
        self.homework_manager.update_homework()

    def get_grades(self) -> list[pronotepy.Grade]:
        return self.grade_manager.get_grades()

    def get_homework(self) -> list[pronotepy.Homework]:
        return self.homework_manager.get_homework()

    def estimate_average(self) -> float | None:
        return self.grade_manager.estimate_average()

    def average_by_subject(self, subject: str) -> float | None:
        return self.grade_manager.average_by_subject(subject)

    def start_scheduler(self, interval_minutes: int = 30) -> None:
        """Démarrer le scheduler."""
        self.scheduler.schedule_check_both(interval_minutes)
        self.scheduler.start()

    def stop_scheduler(self) -> None:
        """Arrêter le scheduler."""
        self.scheduler.stop()

    def register_grade_callback(self, callback) -> None:
        """Enregistrer un callback pour les nouvelles notes."""
        self.scheduler.register_new_grade_callback(callback)

    def register_homework_callback(self, callback) -> None:
        """Enregistrer un callback pour les nouveaux devoirs."""
        self.scheduler.register_new_homework_callback(callback)


def on_new_grades(grades):
    """Callback quand de nouvelles notes arrivent."""
    logger.info(f"🎓 {len(grades)} NOUVELLE(S) NOTE(S) !")
    for grade in grades:
        try:
            subject_name = grade.subject.name if hasattr(grade.subject, 'name') else str(grade.subject)
            grade_value = grade.grade_value if hasattr(grade, 'grade_value') else getattr(grade, 'value', 'N/A')
            out_of = grade.out_of if hasattr(grade, 'out_of') else 'N/A'
            logger.info(f"  📚 {subject_name} - {grade_value}/{out_of}")
        except Exception as e:
            logger.error(f"  Erreur lors du traitement de la note: {e}")


def on_new_homework(homework_list):
    """Callback quand de nouveaux devoirs arrivent."""
    logger.info(f"✏️  {len(homework_list)} NOUVEAU(X) DEVOIR(S) !")
    for homework in homework_list:
        try:
            subject_name = homework.subject.name if hasattr(homework.subject, 'name') else str(homework.subject)
            logger.info(f"  📝 {subject_name} - À rendre: {homework.date}")
        except Exception as e:
            logger.error(f"  Erreur lors du traitement du devoir: {e}")


def main():
    """Lancer le bot."""
    load_dotenv()

    url = os.getenv("PRONOTE_URL")
    username = os.getenv("PRONOTE_USERNAME")
    password = os.getenv("PRONOTE_PASSWORD")
    interval = int(os.getenv("CHECK_INTERVAL", "30"))
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not all([url, username, password]):
        logger.error("❌ Erreur: Variables d'environnement manquantes (.env)")
        return

    logger.info("🚀 Démarrage du bot Pronote...")

    telegram = TelegramNotifier(telegram_token, telegram_chat_id)

    client = PronoteNotifier(url, username, password)

    if not client.is_connected:
        logger.error("❌ Impossible de se connecter à Pronote")
        return

    logger.info("✅ Connecté à Pronote")

    logger.info("📦 Initialisation du cache...")
    client.sync_grades()
    client.sync_homework()
    grades_count = len(client.get_grades())
    homework_count = len(client.get_homework())
    logger.info(f"📦 Cache initialisé: {grades_count} notes, {homework_count} devoirs")

    client.register_grade_callback(on_new_grades)
    client.register_homework_callback(on_new_homework)

    if telegram.enabled:
        logger.info("📱 Notifications Telegram activées")
        client.register_grade_callback(telegram.create_grade_callback())
        client.register_homework_callback(telegram.create_homework_callback())
        telegram.send_startup_message()

    logger.info(f"⏰ Vérification toutes les {interval} minutes")
    client.start_scheduler(interval_minutes=interval)

    logger.info("🟢 Client en cours d'exécution...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Arrêt du bot...")
        telegram.send_shutdown_message()
        client.stop_scheduler()
        client.logout()
        logger.info("✅ Bot arrêté")


if __name__ == "__main__":
    main()
