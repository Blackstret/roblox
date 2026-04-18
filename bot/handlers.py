from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.roblox_api import RobloxAPI
from utils.proxy_checker import ProxyChecker
from utils.database import Database
import logging

router = Router()
db = Database()

logger = logging.getLogger(__name__)


class CookieStates(StatesGroup):
    waiting_for_cookie = State()
    waiting_for_cookies_batch = State()


class ProxyStates(StatesGroup):
    waiting_for_proxy = State()
    waiting_for_proxies_batch = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Start command handler"""
    welcome_text = """
🐱 Welcome to MeowTool Bot!

This bot helps you manage Roblox cookies and proxies.

Available commands:
/addcookie - Add a single Roblox cookie
/addcookies - Add multiple cookies (one per line)
/mycookies - View your stored cookies
/validatecookie - Validate a cookie
/deletecookie - Delete a cookie by ID

/addproxy - Add a single proxy
/addproxies - Add multiple proxies (one per line)
/myproxies - View your stored proxies
/checkproxy - Check if a proxy is working
/deleteproxy - Delete a proxy by ID

/help - Show this help message
"""
    await message.answer(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Help command handler"""
    await cmd_start(message)


@router.message(Command("addcookie"))
async def cmd_add_cookie(message: Message, state: FSMContext):
    """Add a single Roblox cookie"""
    await message.answer("Please send me your Roblox cookie (.ROBLOSECURITY value):")
    await state.set_state(CookieStates.waiting_for_cookie)


@router.message(CookieStates.waiting_for_cookie)
async def process_cookie(message: Message, state: FSMContext):
    """Process the cookie input"""
    cookie = message.text.strip()

    if not cookie:
        await message.answer("Invalid cookie. Please try again.")
        return

    await message.answer("Validating cookie...")

    roblox_api = RobloxAPI()
    result = await roblox_api.validate_cookie(cookie)

    if result.get("valid"):
        await db.add_cookie(
            user_id=message.from_user.id,
            cookie=cookie,
            username=result.get("username"),
            robux=result.get("robux"),
            premium=result.get("premium")
        )

        response = f"""
✅ Cookie added successfully!

Username: {result.get('username')}
User ID: {result.get('user_id')}
Robux: {result.get('robux', 0)}
Premium: {'Yes' if result.get('premium') else 'No'}
"""
        await message.answer(response)
    else:
        await message.answer(f"❌ Invalid cookie: {result.get('error')}")

    await state.clear()


@router.message(Command("addcookies"))
async def cmd_add_cookies_batch(message: Message, state: FSMContext):
    """Add multiple cookies"""
    await message.answer("Please send me your Roblox cookies (one per line):")
    await state.set_state(CookieStates.waiting_for_cookies_batch)


@router.message(CookieStates.waiting_for_cookies_batch)
async def process_cookies_batch(message: Message, state: FSMContext):
    """Process multiple cookies"""
    cookies = [line.strip() for line in message.text.split('\n') if line.strip()]

    if not cookies:
        await message.answer("No valid cookies found. Please try again.")
        return

    await message.answer(f"Processing {len(cookies)} cookies...")

    roblox_api = RobloxAPI()
    valid_count = 0
    invalid_count = 0

    for cookie in cookies:
        result = await roblox_api.validate_cookie(cookie)

        if result.get("valid"):
            await db.add_cookie(
                user_id=message.from_user.id,
                cookie=cookie,
                username=result.get("username"),
                robux=result.get("robux"),
                premium=result.get("premium")
            )
            valid_count += 1
        else:
            invalid_count += 1

    await message.answer(f"""
✅ Batch processing complete!

Valid cookies: {valid_count}
Invalid cookies: {invalid_count}
""")

    await state.clear()


@router.message(Command("mycookies"))
async def cmd_my_cookies(message: Message):
    """View user's stored cookies"""
    cookies = await db.get_user_cookies(message.from_user.id)

    if not cookies:
        await message.answer("You don't have any stored cookies yet.")
        return

    response = "🍪 Your stored cookies:\n\n"

    for cookie_data in cookies:
        response += f"""
ID: {cookie_data['id']}
Username: {cookie_data.get('roblox_username', 'Unknown')}
Robux: {cookie_data.get('robux', 0)}
Premium: {'Yes' if cookie_data.get('premium') else 'No'}
Added: {cookie_data.get('created_at', 'Unknown')}
---
"""

    await message.answer(response)


@router.message(Command("validatecookie"))
async def cmd_validate_cookie(message: Message, state: FSMContext):
    """Validate a stored cookie"""
    cookies = await db.get_user_cookies(message.from_user.id)

    if not cookies:
        await message.answer("You don't have any stored cookies yet.")
        return

    response = "Select a cookie to validate (send the ID):\n\n"
    for cookie_data in cookies:
        response += f"ID {cookie_data['id']}: {cookie_data.get('roblox_username', 'Unknown')}\n"

    await message.answer(response)


@router.message(Command("addproxy"))
async def cmd_add_proxy(message: Message, state: FSMContext):
    """Add a single proxy"""
    await message.answer("Please send me your proxy (format: protocol://ip:port or ip:port):")
    await state.set_state(ProxyStates.waiting_for_proxy)


@router.message(ProxyStates.waiting_for_proxy)
async def process_proxy(message: Message, state: FSMContext):
    """Process the proxy input"""
    proxy = message.text.strip()

    if not proxy:
        await message.answer("Invalid proxy. Please try again.")
        return

    await message.answer("Checking proxy...")

    result = await ProxyChecker.check_proxy(proxy)

    if result.get("working"):
        await db.add_proxy(
            user_id=message.from_user.id,
            proxy=proxy,
            working=True,
            response_time=result.get("response_time")
        )

        response = f"""
✅ Proxy added successfully!

Proxy: {proxy}
Response time: {result.get('response_time')}s
IP: {result.get('ip')}
"""
        await message.answer(response)
    else:
        await message.answer(f"❌ Proxy not working: {result.get('error')}")

    await state.clear()


@router.message(Command("addproxies"))
async def cmd_add_proxies_batch(message: Message, state: FSMContext):
    """Add multiple proxies"""
    await message.answer("Please send me your proxies (one per line):")
    await state.set_state(ProxyStates.waiting_for_proxies_batch)


@router.message(ProxyStates.waiting_for_proxies_batch)
async def process_proxies_batch(message: Message, state: FSMContext):
    """Process multiple proxies"""
    proxies = [line.strip() for line in message.text.split('\n') if line.strip()]

    if not proxies:
        await message.answer("No valid proxies found. Please try again.")
        return

    await message.answer(f"Checking {len(proxies)} proxies...")

    results = await ProxyChecker.check_proxies_batch(proxies)

    working_count = 0
    failed_count = 0

    for result in results:
        if result.get("working"):
            await db.add_proxy(
                user_id=message.from_user.id,
                proxy=result.get("proxy"),
                working=True,
                response_time=result.get("response_time")
            )
            working_count += 1
        else:
            failed_count += 1

    await message.answer(f"""
✅ Batch processing complete!

Working proxies: {working_count}
Failed proxies: {failed_count}
""")

    await state.clear()


@router.message(Command("myproxies"))
async def cmd_my_proxies(message: Message):
    """View user's stored proxies"""
    proxies = await db.get_user_proxies(message.from_user.id, working_only=False)

    if not proxies:
        await message.answer("You don't have any stored proxies yet.")
        return

    response = "🔌 Your stored proxies:\n\n"

    for proxy_data in proxies:
        status = "✅ Working" if proxy_data.get('working') else "❌ Failed"
        response_time = f"{proxy_data.get('response_time', 0)}s" if proxy_data.get('response_time') else "N/A"

        response += f"""
ID: {proxy_data['id']}
Proxy: {proxy_data.get('proxy')}
Status: {status}
Response time: {response_time}
Added: {proxy_data.get('created_at', 'Unknown')}
---
"""

    await message.answer(response)


@router.message(Command("checkproxy"))
async def cmd_check_proxy(message: Message):
    """Check stored proxies"""
    proxies = await db.get_user_proxies(message.from_user.id, working_only=False)

    if not proxies:
        await message.answer("You don't have any stored proxies yet.")
        return

    await message.answer(f"Checking {len(proxies)} proxies...")

    for proxy_data in proxies:
        result = await ProxyChecker.check_proxy(proxy_data['proxy'])

        await db.update_proxy_status(
            proxy_id=proxy_data['id'],
            working=result.get('working', False),
            response_time=result.get('response_time')
        )

    await message.answer("✅ All proxies checked! Use /myproxies to see the results.")
