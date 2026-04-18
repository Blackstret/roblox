import aiohttp
from aiohttp_socks import ProxyConnector
from typing import Optional, Dict, Any
import asyncio


class RobloxAPI:
    BASE_URL = "https://www.roblox.com"
    USERS_URL = "https://users.roblox.com"
    AUTH_URL = "https://auth.roblox.com"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def create_session(self, proxy: Optional[str] = None):
        if proxy:
            connector = ProxyConnector.from_url(proxy)
            self.session = aiohttp.ClientSession(connector=connector)
        else:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def validate_cookie(self, cookie: str, proxy: Optional[str] = None) -> Dict[str, Any]:
        """Validate a Roblox cookie and return account information"""
        await self.create_session(proxy)

        try:
            headers = {
                "Cookie": f".ROBLOSECURITY={cookie}",
                "User-Agent": "Mozilla/5.0"
            }

            async with self.session.get(
                f"{self.USERS_URL}/v1/users/authenticated",
                headers=headers
            ) as response:
                if response.status == 200:
                    user_data = await response.json()

                    # Get additional user info
                    user_id = user_data.get("id")
                    username = user_data.get("name")

                    # Get robux balance
                    robux = await self._get_robux(user_id, headers)

                    # Get premium status
                    premium = await self._get_premium_status(user_id, headers)

                    return {
                        "valid": True,
                        "user_id": user_id,
                        "username": username,
                        "robux": robux,
                        "premium": premium
                    }
                else:
                    return {"valid": False, "error": "Invalid cookie"}

        except Exception as e:
            return {"valid": False, "error": str(e)}

        finally:
            await self.close_session()

    async def _get_robux(self, user_id: int, headers: Dict[str, str]) -> int:
        """Get user's Robux balance"""
        try:
            async with self.session.get(
                f"https://economy.roblox.com/v1/users/{user_id}/currency",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("robux", 0)
        except:
            pass
        return 0

    async def _get_premium_status(self, user_id: int, headers: Dict[str, str]) -> bool:
        """Check if user has premium"""
        try:
            async with self.session.get(
                f"{self.BASE_URL}/v1/users/{user_id}/premium",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("isPremium", False)
        except:
            pass
        return False

    async def refresh_cookie(self, cookie: str, proxy: Optional[str] = None) -> Dict[str, Any]:
        """Attempt to refresh a Roblox cookie"""
        await self.create_session(proxy)

        try:
            headers = {
                "Cookie": f".ROBLOSECURITY={cookie}",
                "User-Agent": "Mozilla/5.0"
            }

            async with self.session.post(
                f"{self.AUTH_URL}/v1/authentication-ticket",
                headers=headers
            ) as response:
                if response.status == 200:
                    ticket = response.headers.get("rbx-authentication-ticket")
                    if ticket:
                        # Use ticket to get new cookie
                        return {"success": True, "ticket": ticket}

                return {"success": False, "error": "Failed to get ticket"}

        except Exception as e:
            return {"success": False, "error": str(e)}

        finally:
            await self.close_session()
