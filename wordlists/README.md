# AdminHunter

Advanced Admin Panel & Login Page Finder for authorised security testing.

## Features

- Built-in 200+ admin path wordlist
- Login form detection using regex
- Redirect tracking
- Custom wordlist support
- Threaded scanning
- Proxy support (Burp/ZAP)
- Custom headers and cookies
- JSON output for automation
- Extension fuzzing (php, html, asp)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/adminhunter.git
cd adminhunter
pip install -r requirements.txt
chmod +x adminhunter.py
```

## Usage

Basic scan:

```bash
python3 adminhunter.py https://example.com
```

Custom wordlist:

```bash
python3 adminhunter.py https://example.com -w wordlists/default.txt
```

With extensions:

```bash
python3 adminhunter.py https://example.com -e php,html,asp
```

Only show login forms:

```bash
python3 adminhunter.py https://example.com --only-login
```

With proxy:

```bash
python3 adminhunter.py https://example.com --proxy http://127.0.0.1:8080
```

Save JSON output:

```bash
python3 adminhunter.py https://example.com -o results.json
```

## Options

| Flag | Description |
|------|-------------|
| `-w, --wordlist` | Custom wordlist file path |
| `-t, --threads` | Number of concurrent threads (default 25) |
| `--timeout` | Request timeout in seconds (default 6) |
| `-d, --delay` | Delay between requests (default 0) |
| `-e, --extensions` | Append extensions to paths |
| `--headers` | Custom headers `key=value;key2=value2` |
| `--proxy` | HTTP/HTTPS proxy |
| `--follow` | Follow redirects |
| `-o, --output` | Save results to JSON |
| `--only-login` | Only show pages with login form |
| `--no-color` | Disable colored output |

## Custom Wordlists

Add your own wordlists in the `wordlists/` folder and pass with `-w` flag:

```bash
python3 adminhunter.py https://example.com -w wordlists/my_custom_list.txt
```

Wordlist format: one path per line, no leading slash.

## Legal Disclaimer

This tool is intended for authorised security testing only. Using it against systems without explicit written permission is illegal. The author assumes no liability for misuse.

## License

MIT License - see LICENSE file
