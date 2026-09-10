#!/usr/bin/env python3
"""
AdminHunter - Advanced Admin Panel & Login Page Finder
Author: Your Name
License: MIT
For authorised security testing only.
"""

import sys
import os
import argparse
import threading
import time
import queue
import re
import json
from urllib.parse import urljoin
from datetime import datetime

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("[!] requests missing. Install: pip install requests")
    sys.exit(1)

R = "\033[0m"
G = "\033[92m"
B = "\033[94m"
Y = "\033[93m"
RD = "\033[91m"
M = "\033[95m"
C = "\033[96m"

def colored(code):
    if 200 <= code < 300:
        return f"{G}{code}{R}"
    if 300 <= code < 400:
        return f"{B}{code}{R}"
    if 400 <= code < 500:
        return f"{Y}{code}{R}"
    return f"{RD}{code}{R}"

LOGIN_PATTERNS = [
    r'<input[^>]+type=["\']password["\']',
    r'<input[^>]+name=["\'](pass|password|passwd|pwd)["\']',
    r'<form[^>]+(login|signin|auth)',
    r'type=["\']password["\']',
    r'name=["\'](username|user|email|login)["\']',
]

TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)

def has_login_form(html):
    if not html:
        return False
    low = html.lower()
    return any(re.search(p, low) for p in LOGIN_PATTERNS)

def extract_title(html):
    if not html:
        return ""
    m = TITLE_RE.search(html)
    return m.group(1).strip()[:60] if m else ""

def load_default_wordlist():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, "wordlists", "default.txt")
    if os.path.exists(default_path):
        with open(default_path, encoding="utf-8", errors="ignore") as f:
            return [ln.strip() for ln in f if ln.strip()]
    return []

class AdminHunter:
    def __init__(self, base_url, wordlist, threads=25, timeout=6, delay=0,
                 headers=None, cookies=None, proxy=None, follow=False,
                 user_agent=None):
        self.base_url = base_url.rstrip('/')
        self.wordlist = wordlist
        self.threads = threads
        self.timeout = timeout
        self.delay = delay
        self.follow = follow
        self.q = queue.Queue()
        self.results = []
        self.lock = threading.Lock()
        self.running = True

        self.session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.4,
                        status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        ua = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
        self.session.headers.update({
            "User-Agent": ua,
            "Accept": "*/*",
            "Connection": "close"
        })
        if headers:
            self.session.headers.update(headers)
        if cookies:
            self.session.cookies.update(cookies)
        self.proxies = {"http": proxy, "https": proxy} if proxy else None

    def check(self, path):
        if not self.running:
            return
        if self.delay > 0:
            time.sleep(self.delay)
        url = urljoin(self.base_url + '/', path.lstrip('/'))
        try:
            r = self.session.get(url, timeout=self.timeout,
                                 allow_redirects=self.follow,
                                 proxies=self.proxies)
            code = r.status_code
            if code in (404, 410):
                return
            body = r.text[:8000] if code == 200 else ""
            login = has_login_form(body)
            title = extract_title(body)
            length = len(r.content)
            with self.lock:
                self.results.append({
                    "url": url,
                    "path": path,
                    "status": code,
                    "length": length,
                    "title": title,
                    "login": login,
                    "redirect": r.headers.get("Location", "") if code in (301, 302, 303, 307, 308) else ""
                })
                tag = f"{M}[LOGIN]{R}" if login else "       "
                redir = f" -> {r.headers.get('Location', '')[:40]}" if code in (301, 302) else ""
                print(f"{colored(code)}  {path:42}  {length:>7}B  {title[:30]:30}  {tag}{redir}")
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.SSLError:
            pass
        except Exception:
            pass

    def worker(self):
        while self.running:
            try:
                path = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            self.check(path)
            self.q.task_done()

    def scan(self):
        for w in self.wordlist:
            self.q.put(w)
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            threads.append(t)
        self.q.join()
        self.running = False
        for t in threads:
            t.join(timeout=0.5)
        return self.results

def parse_kv(s):
    if not s:
        return None
    d = {}
    for pair in s.split(';'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            d[k.strip()] = v.strip()
    return d

def main():
    ap = argparse.ArgumentParser(
        description="AdminHunter - Admin panel & login page finder",
        epilog="Example: adminhunter https://target.com -t 30 -e php"
    )
    ap.add_argument("url", help="Target base URL")
    ap.add_argument("-w", "--wordlist", help="Custom wordlist file")
    ap.add_argument("-t", "--threads", type=int, default=25)
    ap.add_argument("--timeout", type=int, default=6)
    ap.add_argument("-d", "--delay", type=float, default=0)
    ap.add_argument("-e", "--extensions", help="Append extensions: php,html,asp")
    ap.add_argument("--headers", help="Headers: Cookie=abc;Auth=xyz")
    ap.add_argument("--proxy", help="Proxy URL")
    ap.add_argument("--follow", action="store_true")
    ap.add_argument("-o", "--output", help="Save JSON results")
    ap.add_argument("--only-login", action="store_true")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args()

    if args.no_color:
        global R, G, B, Y, RD, M, C
        R = G = B = Y = RD = M = C = ""

    if args.wordlist:
        if not os.path.exists(args.wordlist):
            print(f"[!] Wordlist not found: {args.wordlist}")
            sys.exit(1)
        with open(args.wordlist, encoding="utf-8", errors="ignore") as f:
            wl = [ln.strip() for ln in f if ln.strip()]
        print(f"[*] Loaded {len(wl)} entries from {args.wordlist}")
    else:
        wl = load_default_wordlist()
        if not wl:
            print("[!] No default wordlist found in wordlists/default.txt")
            sys.exit(1)
        print(f"[*] Using default wordlist ({len(wl)} entries)")

    if args.extensions:
        exts = [e.strip().lstrip('.') for e in args.extensions.split(',') if e.strip()]
        extra = []
        for w in wl:
            if '.' not in os.path.basename(w):
                for e in exts:
                    extra.append(f"{w}.{e}")
        wl.extend(extra)
        print(f"[*] With extensions: {len(wl)} total entries")

    if not args.url.startswith(("http://", "https://")):
        args.url = "https://" + args.url

    headers = parse_kv(args.headers) if args.headers else None

    print(f"[*] Target  : {args.url}")
    print(f"[*] Threads : {args.threads}")
    print(f"[*] Timeout : {args.timeout}s")
    if args.proxy:
        print(f"[*] Proxy   : {args.proxy}")
    print("-" * 100)

    hunter = AdminHunter(
        base_url=args.url,
        wordlist=wl,
        threads=args.threads,
        timeout=args.timeout,
        delay=args.delay,
        headers=headers,
        proxy=args.proxy,
        follow=args.follow
    )

    start = time.time()
    try:
        results = hunter.scan()
    except KeyboardInterrupt:
        print("\n[!] Interrupted.")
        hunter.running = False
        results = hunter.results
    elapsed = time.time() - start

    hits = results
    if args.only_login:
        hits = [r for r in results if r["login"]]

    print("-" * 100)
    print(f"[*] Scanned in {elapsed:.2f}s  |  Found {len(results)} paths  |  "
          f"Login forms: {len([r for r in results if r['login']])}")

    if hits:
        print(f"\n{C}=== HITS ==={R}")
        for r in sorted(hits, key=lambda x: x["status"]):
            tag = f" {M}[LOGIN]{R}" if r["login"] else ""
            print(f"  {colored(r['status'])}  {r['url']}{tag}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "target": args.url,
                "scan_time": str(datetime.now()),
                "total_found": len(results),
                "results": results
            }, f, indent=2)
        print(f"\n[*] Saved JSON: {args.output}")

if __name__ == "__main__":
    main()
