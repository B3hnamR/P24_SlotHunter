import asyncio
from typing import List
from telegram import Bot
from telegram.error import Forbidden, BadRequest, TimedOut, NetworkError

from src.database.database import db_session
from src.database.models import Doctor, Subscription, AppointmentLog
from src.api.models import Appointment
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("Notifier")

async def send_appointment_alert(bot: Bot, doctor: Doctor, appointments: List[Appointment]):
    """ارسال اطلاع‌رسانی نوبت جدید"""
    try:
        with db_session() as session:
            db_doctor = session.query(Doctor).filter(Doctor.slug == doctor.slug).first()
            if not db_doctor:
                logger.warning(f"⚠️ دکتر {doctor.name} در دیتابیس یافت نشد")
                return

            active_subscriptions = session.query(Subscription).filter(
                Subscription.doctor_id == db_doctor.id,
                Subscription.is_active == True
            ).all()

            if not active_subscriptions:
                logger.info(f"📭 هیچ مشترکی برای {doctor.name} وجود ندارد")
                return

            message = MessageFormatter.appointment_alert_message(doctor, appointments)
            sent_count = 0
            failed_count = 0

            for subscription in active_subscriptions:
                try:
                    await bot.send_message(
                        chat_id=subscription.user.telegram_id,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    sent_count += 1
                    await asyncio.sleep(0.1)
                except Forbidden:
                    logger.warning(f"🚫 کاربر {subscription.user.telegram_id} ربات را بلاک کرده. اشتراک غیرفعال می‌شود.")
                    subscription.is_active = False
                    session.commit()
                    failed_count += 1
                except BadRequest as e:
                    logger.error(f"❌ خطای BadRequest برای کاربر {subscription.user.telegram_id}: {e}. اشتراک غیرفعال می‌شود.")
                    subscription.is_active = False
                    session.commit()
                    failed_count += 1
                except (TimedOut, NetworkError) as e:
                    logger.warning(f"⚠️ خطای شبکه در ارسال به {subscription.user.telegram_id}: {e}. این پیام ارسال نشد.")
                    failed_count += 1
                except Exception as e:
                    logger.exception(f"❌ خطای پیش‌بینی نشده در ارسال به {subscription.user.telegram_id}: {e}")
                    failed_count += 1

            logger.info(
                f"📢 اطلاع‌رسانی {doctor.name}: "
                f"✅ {sent_count} موفق، ❌ {failed_count} ناموفق"
            )

            from datetime import datetime
            appointment_log = AppointmentLog(
                doctor_id=db_doctor.id,
                appointment_date=appointments[0].start_datetime,
                appointment_count=len(appointments),
                notified_users=sent_count
            )
            session.add(appointment_log)
            session.commit()

    except Exception as e:
        logger.exception(f"❌ خطا در ارسال اطلاع‌رسانی: {e}")
