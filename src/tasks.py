import asyncio
from telegram import Bot
from src.celery_app import celery_app
from src.database.database import db_session
from src.database.models import Doctor as DBDoktor
from src.api.paziresh_client import PazireshAPI
from src.telegram_bot.notifier import send_appointment_alert
from src.utils.config import Config
from src.api.models import Doctor as ApiDoctor

# Load config and create a global bot instance
config = Config()
bot = Bot(token=config.telegram_bot_token)

@celery_app.task
def monitor_all_doctors():
    """
    The main task that gets a list of all active doctors and creates a child task for each one.
    """
    with db_session() as session:
        active_doctors = session.query(DBDoktor).filter(DBDoktor.is_active == True).all()
        for doctor in active_doctors:
            check_doctor_availability.delay(doctor.id)

@celery_app.task
def check_doctor_availability(doctor_id: int):
    """
    The child task that checks the availability of a specific doctor.
    """
    with db_session() as session:
        doctor = session.query(DBDoktor).filter(DBDoktor.id == doctor_id).first()
        if not doctor:
            return

    try:
        # Convert DB model to API model
        api_doctor = ApiDoctor(
            name=doctor.name,
            slug=doctor.slug,
            center_id=doctor.center_id,
            service_id=doctor.service_id,
            user_center_id=doctor.user_center_id,
            terminal_id=doctor.terminal_id,
        )
        client = PazireshAPI(doctor=api_doctor)
        appointments = client.get_available_appointments()
        if appointments:
            asyncio.run(send_appointment_alert(bot, doctor, appointments))
    except Exception as e:
        print(f"Error checking doctor {doctor.name}: {e}")
