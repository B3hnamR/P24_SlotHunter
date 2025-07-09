#!/usr/bin/env python3
"""
Fix admin markdown issue
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def fix_admin_markdown():
    """Fix the markdown parsing issue in admin handlers"""
    
    # Read the current file
    with open('src/telegram_bot/admin_handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the problematic admin_text section
    old_text = '''        admin_text = """
🔧 **پنل مدیریت P24_SlotHunter**

انتخاب کنید:
        """
        
        await update.message.reply_text(admin_text, reply_markup=reply_markup, parse_mode='Markdown')'''
    
    new_text = '''        admin_text = "🔧 پنل مدیریت P24_SlotHunter\\n\\nانتخاب کنید:"
        
        await update.message.reply_text(admin_text, reply_markup=reply_markup)'''
    
    # Replace the content
    content = content.replace(old_text, new_text)
    
    # Also fix other potential markdown issues
    content = content.replace('parse_mode=\'Markdown\'', 'parse_mode=\'HTML\'')
    content = content.replace('**', '<b>', 1).replace('**', '</b>', 1)
    
    # Write the fixed content back
    with open('src/telegram_bot/admin_handlers.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Admin markdown issue fixed!")

if __name__ == "__main__":
    fix_admin_markdown()