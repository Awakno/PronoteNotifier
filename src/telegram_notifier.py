"""
Module de notifications Telegram pour Pronote Notifier
"""

import logging
import os
from typing import Callable
from telegram import Bot
from telegram.error import TelegramError
import asyncio

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Gestionnaire de notifications Telegram."""

    def __init__(self, token: str, chat_id: str) -> None:
        """
        Initialiser le notifier Telegram.
        
        Args:
            token: Token du bot Telegram (depuis BotFather)
            chat_id: ID du chat/groupe pour recevoir les messages
        """
        self.token = token
        self.chat_id = chat_id
        self.bot: Bot | None = None
        self.enabled = False

        if token and chat_id:
            try:
                self.bot = Bot(token=token)
                self.enabled = True
                logger.info("✅ Notifier Telegram initialisé")
            except Exception as e:
                logger.error(f"❌ Erreur d'initialisation Telegram: {e}")
                self.enabled = False

    def _send_message_sync(self, message: str) -> bool:
        loop = asyncio.get_event_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True,
            ),
            loop
        )
        try:
            future.result(timeout=10)
            return True
        except Exception as e:
            logger.error(f"❌ Erreur Telegram: {e}")
            return False

    def create_grade_callback(self) -> Callable:
        """Créer un callback pour les nouvelles notes."""

        def callback(grades):
            if not self.enabled or not self.bot:
                return

            try:
                message = f"🎓 <b>{len(grades)} NOUVELLE(S) NOTE(S) !</b>\n\n"
                for grade in grades:
                    try:
                        subject_name = grade.subject.name if hasattr(grade.subject, 'name') else str(grade.subject)
                        grade_value = grade.grade_value if hasattr(grade, 'grade_value') else getattr(grade, 'value', 'N/A')
                        out_of = grade.out_of if hasattr(grade, 'out_of') else 'N/A'
                        
                        message += f"📚 <b>{subject_name}</b>\n"
                        message += f"   Note: {grade_value}/{out_of}"
                        if hasattr(grade, 'comment') and grade.comment:
                            message += f"\n   Commentaire: {grade.comment}"
                        message += "\n\n"
                    except Exception as e:
                        logger.error(f"Erreur traitement note: {e}")

                self._send_message_sync(message)
            except Exception as e:
                logger.error(f"Erreur callback grades: {e}")

        return callback

    def create_homework_callback(self) -> Callable:
        """Créer un callback pour les nouveaux devoirs."""

        def callback(homework_list):
            if not self.enabled or not self.bot:
                return

            try:
                message = f"✏️ <b>{len(homework_list)} NOUVEAU(X) DEVOIR(S) !</b>\n\n"
                for homework in homework_list:
                    try:
                        subject_name = homework.subject.name if hasattr(homework.subject, 'name') else str(homework.subject)
                        
                        message += f"📝 <b>{subject_name}</b>\n"
                        message += f"   À rendre: {homework.date}"
                        if hasattr(homework, 'description') and homework.description:
                            message += f"\n   {homework.description}"
                        message += "\n\n"
                    except Exception as e:
                        logger.error(f"Erreur traitement devoir: {e}")

                self._send_message_sync(message)
            except Exception as e:
                logger.error(f"Erreur callback homework: {e}")

        return callback

    def send_startup_message(self) -> None:
        """Envoyer un message de démarrage."""
        if not self.enabled:
            return

        message = "🟢 <b>Bot Pronote Notifier démarré</b>\n\n"
        message += "Le monitoring des notes et devoirs est activé."

        self._send_message_sync(message)

    def send_shutdown_message(self) -> None:
        """Envoyer un message d'arrêt."""
        if not self.enabled:
            return

        message = "⏹️ <b>Bot Pronote Notifier arrêté</b>"

        self._send_message_sync(message)
