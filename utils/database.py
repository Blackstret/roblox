from supabase import create_client, Client
import os
from typing import Optional, List, Dict, Any


class Database:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.client: Client = create_client(supabase_url, supabase_key)

    async def add_cookie(self, user_id: int, cookie: str, username: Optional[str] = None,
                        robux: Optional[int] = None, premium: Optional[bool] = None) -> Dict[str, Any]:
        """Add a Roblox cookie to the database"""
        data = {
            "telegram_user_id": user_id,
            "cookie": cookie,
            "roblox_username": username,
            "robux": robux,
            "premium": premium,
            "valid": True
        }

        result = self.client.table("cookies").insert(data).execute()
        return result.data[0] if result.data else None

    async def get_user_cookies(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all cookies for a user"""
        result = self.client.table("cookies")\
            .select("*")\
            .eq("telegram_user_id", user_id)\
            .eq("valid", True)\
            .execute()

        return result.data

    async def update_cookie_status(self, cookie_id: int, valid: bool) -> None:
        """Update cookie validation status"""
        self.client.table("cookies")\
            .update({"valid": valid})\
            .eq("id", cookie_id)\
            .execute()

    async def delete_cookie(self, cookie_id: int) -> None:
        """Delete a cookie"""
        self.client.table("cookies")\
            .delete()\
            .eq("id", cookie_id)\
            .execute()

    async def add_proxy(self, user_id: int, proxy: str, working: bool = True,
                       response_time: Optional[float] = None) -> Dict[str, Any]:
        """Add a proxy to the database"""
        data = {
            "telegram_user_id": user_id,
            "proxy": proxy,
            "working": working,
            "response_time": response_time
        }

        result = self.client.table("proxies").insert(data).execute()
        return result.data[0] if result.data else None

    async def get_user_proxies(self, user_id: int, working_only: bool = True) -> List[Dict[str, Any]]:
        """Get all proxies for a user"""
        query = self.client.table("proxies")\
            .select("*")\
            .eq("telegram_user_id", user_id)

        if working_only:
            query = query.eq("working", True)

        result = query.execute()
        return result.data

    async def update_proxy_status(self, proxy_id: int, working: bool,
                                 response_time: Optional[float] = None) -> None:
        """Update proxy status"""
        data = {"working": working}
        if response_time is not None:
            data["response_time"] = response_time

        self.client.table("proxies")\
            .update(data)\
            .eq("id", proxy_id)\
            .execute()

    async def delete_proxy(self, proxy_id: int) -> None:
        """Delete a proxy"""
        self.client.table("proxies")\
            .delete()\
            .eq("id", proxy_id)\
            .execute()
