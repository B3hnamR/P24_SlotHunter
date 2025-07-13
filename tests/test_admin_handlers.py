import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update, User, CallbackQuery
from telegram.ext import ConversationHandler, Application, ContextTypes
from src.telegram_bot.admin_handlers import TelegramAdminHandlers
from src.telegram_bot.constants import ConversationStates

@pytest.mark.asyncio
async def test_start_add_doctor_as_admin():
    """
    Tests the start_add_doctor conversation flow for an admin user.
    """
    # Mock admin user and query
    admin_user = User(id=123, first_name="Admin", is_bot=False)
    query = AsyncMock(spec=CallbackQuery)
    query.from_user = admin_user
    update = Update(1, callback_query=query)
    context = ContextTypes.DEFAULT_TYPE(application=AsyncMock(spec=Application), chat_id=123, user_id=123)

    # Patch the admin check to always return True
    with patch('src.telegram_bot.user_roles.user_role_manager.is_admin_or_higher', return_value=True):
        # Call the handler
        next_state = await TelegramAdminHandlers.start_add_doctor(update, context)

        # Assertions
        query.answer.assert_called_once()
        query.edit_message_text.assert_called_once_with(
            "🔗 افزودن دکتر جدید\n\n"
            "لینک صفحه دکتر در پذیرش۲۴ را ارسال کنید:\n\n"
            "✅ فرمت‌های پشتیبانی شده:\n"
            "• https://www.paziresh24.com/dr/دکتر-نام-0/\n"
            "• https://www.paziresh24.com/dr/%D8%AF%DA%A9%D8%AA%D8%B1-...\n\n"
            "برای لغو: /cancel"
        )
        assert next_state == ConversationStates.ADD_DOCTOR_LINK.value

@pytest.mark.asyncio
async def test_start_add_doctor_as_non_admin():
    """
    Tests that a non-admin user cannot start the add_doctor conversation.
    """
    # Mock non-admin user and query
    non_admin_user = User(id=456, first_name="User", is_bot=False)
    query = AsyncMock(spec=CallbackQuery)
    query.from_user = non_admin_user
    update = Update(1, callback_query=query)
    context = ContextTypes.DEFAULT_TYPE(application=AsyncMock(spec=Application), chat_id=456, user_id=456)

    # Patch the admin check to always return False
    with patch('src.telegram_bot.user_roles.user_role_manager.is_admin_or_higher', return_value=False):
        # Call the handler
        next_state = await TelegramAdminHandlers.start_add_doctor(update, context)

        # Assertions
        query.answer.assert_called_once()
        query.edit_message_text.assert_called_once_with("❌ شما دسترسی ادمین ندارید.")
        assert next_state == ConversationHandler.END
