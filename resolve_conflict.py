
#!/usr/bin/env python3
"""
حل مشکل Telegram Conflict
"""
import asyncio
import sys
import time
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

async def clear_telegram_updates():
    """پاک کردن pending updates"""
    print("🧹 Clearing Telegram Updates")
    print("-" * 30)

    try:
        from src.utils.config import Config
        import httpx

        config = Config()

        # دریافت و پاک کردن pending updates
        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/getUpdates"

        async with httpx.AsyncClient(timeout=30) as client:
            print("📥 Getting pending updates...")

            # دریافت updates با offset بالا برای پاک کردن
            params = {
                "offset": -1,  # آخرین update
                "timeout": 1   # timeout کوتاه
            }

            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    updates = data.get('result', [])
                    print(f"📊 Found {len(updates)} pending updates")

                    if updates:
                        # پاک کردن با offset آخرین update + 1
                        last_update_id = max(update['update_id'] for update in updates)
                        clear_params = {
                            "offset": last_update_id + 1,
                            "timeout": 1
                        }

                        clear_response = await client.get(url, params=clear_params)
                        if clear_response.status_code == 200:
                            print("✅ Pending updates cleared")
                        else:
                            print("⚠️ Could not clear updates")
                    else:
                        print("✅ No pending updates")

                    return True
                else:
                    print(f"❌ API Error: {data.get('description')}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Clear updates failed: {e}")
        return False

async def wait_for_conflict_resolution():
    """انتظار برای حل conflict"""
    print("\n⏳ Waiting for Conflict Resolution")
    print("-" * 35)

    try:
        from src.utils.config import Config
        import httpx

        config = Config()
        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/getMe"

        max_attempts = 10
        wait_time = 5

        for attempt in range(1, max_attempts + 1):
            print(f"🔄 Attempt {attempt}/{max_attempts}...")

            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(url)

                    if response.status_code == 200:
                        data = response.json()
                        if data.get('ok'):
                            print("✅ Bot connection restored!")
                            return True

                    print(f"⏳ Waiting {wait_time} seconds...")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                print(f"⚠️ Attempt {attempt} failed: {e}")
                await asyncio.sleep(wait_time)

        print("❌ Could not resolve conflict")
        return False

    except Exception as e:
        print(f"❌ Wait failed: {e}")
        return False

def kill_conflicting_processes():
    """کشتن process های مشکوک"""
    print("\n🔍 Checking for Conflicting Processes")
    print("-" * 40)

    import subprocess

    try:
        # جستجوی process های python مرتبط با telegram
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

        telegram_processes = []
        for line in result.stdout.split('\n'):
            if ('python' in line and
                ('telegram' in line.lower() or 'bot' in line.lower()) and
                'P24_SlotHunter' not in line):
                telegram_processes.append(line.strip())

        if telegram_processes:
            print(f"⚠️ Found {len(telegram_processes)} suspicious processes:")
            for proc in telegram_processes:
                print(f"  {proc}")

            print("\n💡 You may need to manually kill these processes")
            print("   Use: kill -9 <PID>")
        else:
            print("✅ No conflicting processes found")

        return len(telegram_processes) == 0

    except Exception as e:
        print(f"❌ Process check failed: {e}")
        return True

async def main():
    print("🔧 P24_SlotHunter Conflict Resolver")
    print("=" * 45)

    # بررسی محیط
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("❌ Virtual environment not active")
        print("💡 Run: source venv/bin/activate")
        return

    print("✅ Virtual environment active")

    # بررسی process ها
    kill_conflicting_processes()

    # پاک کردن updates
    await clear_telegram_updates()

    # انتظار برای حل conflict
    resolved = await wait_for_conflict_resolution()

    print("\n" + "=" * 45)
    if resolved:
        print("🎉 Conflict resolved!")
        print("\n🚀 You can now restart the service:")
        print("   ./server_manager.sh restart")
    else:
        print("❌ Could not resolve conflict automatically")
        print("\n🔧 Manual steps:")
        print("1. Stop the service: ./server_manager.sh stop")
        print("2. Wait 30 seconds")
        print("3. Start the service: ./server_manager.sh start")

if __name__ == "__main__":
    asyncio.run(main())