import asyncio
import json
import time
import urllib.request
import aiohttp
from aiohttp_socks import ProxyConnector

# ==========================================
# لیست منابع (می‌توانید کم یا زیاد کنید)
# ==========================================
SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt",
    "https://raw.githubusercontent.com/Boster12/roblox-checker/main/proxies.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt"
]

TEST_URL = "http://httpbin.org/ip"
TIMEOUT = 5  # حداکثر زمان انتظار برای هر پروکسی (ثانیه)

def get_raw_proxies():
    """استخراج تمام پروکسی‌ها از لینک‌ها و حذف تکراری‌ها"""
    raw_proxies = set()
    for url in SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                text = response.read().decode('utf-8')
                for line in text.splitlines():
                    proxy = line.strip()
                    if proxy and ":" in proxy:
                        # حذف پیشوند احتمالی برای یکدست‌سازی داده‌های خام ورودی
                        if "://" in proxy:
                            proxy = proxy.split("://")[-1]
                        raw_proxies.add(proxy)
            print(f"[+] Fetched from {url}")
        except Exception as e:
            print(f"[-] Failed to fetch from {url}: {e}")
    return list(raw_proxies)

async def check_proxy(proxy, semaphore):
    """تست زنده بودن پروکسی و محاسبه پینگ"""
    async with semaphore:
        proxy_url = f"socks5://{proxy}"
        try:
            connector = ProxyConnector.from_url(proxy_url)
            start_time = time.time()
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(TEST_URL, timeout=TIMEOUT) as response:
                    if response.status == 200:
                        ping = round((time.time() - start_time) * 1000) # تبدیل به میلی‌ثانیه
                        return {"proxy": proxy, "ping": ping}
        except:
            return None
        return None

async def main():
    print("Gathering proxies...")
    proxies = get_raw_proxies()
    print(f"Total unique proxies found: {len(proxies)}")
    
    print("Testing proxies... (This might take a few minutes)")
    semaphore = asyncio.Semaphore(300) 
    
    tasks = [check_proxy(p, semaphore) for p in proxies]
    results = await asyncio.gather(*tasks)
    
    # فیلتر کردن پروکسی‌های مرده (None) و مرتب‌سازی بر اساس پینگ
    working_proxies = [r for r in results if r is not None]
    working_proxies.sort(key=lambda x: x["ping"])
    
    print(f"Working proxies: {len(working_proxies)}")
    
    # استخراج آی‌پی و پورت و اضافه کردن پیشوند socks5:// به خروجی نهایی
    final_list = [f"socks5://{item['proxy']}" for item in working_proxies]
    
    # ذخیره در فایل JSON (هر خط یک پروکسی به همراه ساختار آرایه)
    with open("Socks5.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2)
    print("Saved to Socks5.json")

if __name__ == "__main__":
    asyncio.run(main())
