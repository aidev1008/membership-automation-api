#!/usr/bin/env python3
"""
Manual demo script - opens ACT Strategic login page and keeps it open
for manual testing and inspection.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def manual_demo():
    """Opens ACT Strategic and keeps browser open for manual interaction."""
    
    load_dotenv()
    username = os.getenv('SCHMICK_USER', '')
    password = os.getenv('SCHMICK_PASS', '')
    
    print("🎭 Manual ACT Strategic Demo")
    print("=" * 40)
    print("Opening ACT Strategic login page...")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
    print("=" * 40)
    
    async with async_playwright() as playwright:
        try:
            # Use regular Chromium with simpler settings
            browser = await playwright.chromium.launch(
                headless=False,
                slow_mo=1000,
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            print("🌐 Navigating to ACT Strategic...")
            await page.goto("https://actstrategic.ai/myaccount/", timeout=30000)
            
            print("✅ Page loaded successfully!")
            print(f"📄 Title: {await page.title()}")
            print(f"🔗 URL: {page.url}")
            
            print("\n💡 INSTRUCTIONS:")
            print("1. The browser should be open now showing ACT Strategic login")
            print("2. You can manually test the login with your credentials:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print("3. The browser will stay open for 2 minutes")
            print("4. Close this terminal or press Ctrl+C to stop")
            
            # Keep browser open for manual testing
            print(f"\n⏰ Browser will stay open for 120 seconds...")
            await page.wait_for_timeout(120000)  # 2 minutes
            
        except KeyboardInterrupt:
            print("\n👋 Manual demo stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("🏁 Demo completed!")

if __name__ == "__main__":
    asyncio.run(manual_demo())