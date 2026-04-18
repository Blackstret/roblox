import aiohttp
from aiohttp_socks import ProxyConnector
from typing import Dict, Any, Optional
import asyncio
import time


class ProxyChecker:
    TEST_URL = "https://httpbin.org/ip"
    TIMEOUT = 10

    @staticmethod
    async def check_proxy(proxy: str) -> Dict[str, Any]:
        """Check if a proxy is working"""
        start_time = time.time()

        try:
            # Determine proxy type
            if proxy.startswith("http://") or proxy.startswith("https://"):
                connector = ProxyConnector.from_url(proxy)
            elif proxy.startswith("socks4://") or proxy.startswith("socks5://"):
                connector = ProxyConnector.from_url(proxy)
            else:
                # Try to auto-detect
                connector = ProxyConnector.from_url(f"http://{proxy}")

            timeout = aiohttp.ClientTimeout(total=ProxyChecker.TIMEOUT)

            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(ProxyChecker.TEST_URL) as response:
                    if response.status == 200:
                        elapsed = time.time() - start_time
                        data = await response.json()

                        return {
                            "working": True,
                            "proxy": proxy,
                            "response_time": round(elapsed, 2),
                            "ip": data.get("origin", "unknown")
                        }

            return {
                "working": False,
                "proxy": proxy,
                "error": "Non-200 status code"
            }

        except asyncio.TimeoutError:
            return {
                "working": False,
                "proxy": proxy,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "working": False,
                "proxy": proxy,
                "error": str(e)
            }

    @staticmethod
    async def check_proxies_batch(proxies: list[str], max_concurrent: int = 10) -> list[Dict[str, Any]]:
        """Check multiple proxies concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def check_with_limit(proxy: str):
            async with semaphore:
                return await ProxyChecker.check_proxy(proxy)

        tasks = [check_with_limit(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)

        return results
