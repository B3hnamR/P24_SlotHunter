"""
Simple admin handler for debugging
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger("SimpleAdmin")

class SimpleAdminHandler:
    """Simple admin handler for testing"""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """Check if user is admin"""
        try:
            config = Config()
            admin_chat_id = config.admin_chat_id
            logger.info(f"Checking admin access: user_id={user_id}, admin_chat_id={admin_chat_id}")
            return user_id == admin_chat_id
        except Exception as e:
            logger.error(f"Error checking admin access: {e}")
            return False
    
    @staticmethod
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        try:
            user_id = update.effective_user.id
            logger.info(f"Admin command from user: {user_id}")
            
            if not SimpleAdminHandler.is_admin(user_id):
                await update.message.reply_text("❌ You don't have admin access.")
                return
            
            keyboard = [
                [InlineKeyboardButton("📊 System Stats", callback_data="simple_admin_stats")],
                [InlineKeyboardButton("👥 User Management", callback_data="simple_admin_users")],
                [InlineKeyboardButton("🔧 Settings", callback_data="simple_admin_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            admin_text = """
🔧 **P24_SlotHunter Admin Panel**

Welcome to the admin panel!

Choose an option:
            """
            
            await update.message.reply_text(admin_text, reply_markup=reply_markup, parse_mode='Markdown')
            logger.info("Admin panel sent successfully")
            
        except Exception as e:
            logger.error(f"Error in admin command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            if not SimpleAdminHandler.is_admin(user_id):
                await query.edit_message_text("❌ You don't have admin access.")
                return
            
            if query.data == "simple_admin_stats":
                await query.edit_message_text("📊 **System Statistics**\n\nSystem is running normally.")
            elif query.data == "simple_admin_users":
                await query.edit_message_text("👥 **User Management**\n\nUser management features coming soon.")
            elif query.data == "simple_admin_settings":
                await query.edit_message_text("🔧 **Settings**\n\nSettings management coming soon.")
            
        except Exception as e:
            logger.error(f"Error in admin callback: {e}")
            await query.edit_message_text(f"❌ Error: {str(e)}")