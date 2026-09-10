# Wordlists

This directory contains wordlists used by AdminHunter for admin panel discovery.

## Built-in Wordlist

The `default.txt` file is the built-in wordlist that comes pre-packaged with AdminHunter. It contains 200+ common admin panel paths, login pages, and CMS-specific endpoints. This list is automatically loaded when you run the tool without the `-w` flag.

## Adding Custom Wordlists

You can add your own wordlists to this directory. Simply create a new `.txt` file with one path per line.

### Format Requirements

- One path per line
- No leading slash (`admin` is correct, `/admin` is incorrect)
- No trailing slash (`admin` is correct, `admin/` is incorrect)
- Empty lines will be ignored
- Lines starting with `#` are not treated as comments by the tool

### Example Custom Wordlist

Create a file called `my_custom.txt`:

```
admin
administrator
admin/login
admin/dashboard
wp-admin
wp-login.php
phpmyadmin
cpanel
webmail
backend
internal
secret-panel
```

### Using a Custom Wordlist

Run AdminHunter with the `-w` flag pointing to your custom wordlist:

```bash
python3 adminhunter.py https://target.com -w wordlists/my_custom.txt
```

You can also use wordlists located anywhere on your system:

```bash
python3 adminhunter.py https://target.com -w /sdcard/wordlists/admin.txt
```

## Recommended Wordlist Sources

If you need larger and more comprehensive wordlists, download them from these trusted sources:

### SecLists (Recommended)

The most popular collection of security testing wordlists.

```bash
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O seclists_common.txt
```

Other useful lists from SecLists:

- `Discovery/Web-Content/directory-list-2.3-medium.txt` - Medium directory list
- `Discovery/Web-Content/raft-medium-directories.txt` - RAFT directory list
- `Discovery/Web-Content/CMS/wp-plugins.fuzz.txt` - WordPress plugins
- `Discovery/Web-Content/CMS/joomla.txt` - Joomla paths

### Assetnote Wordlists

High-quality wordlists for modern web applications.

- Website: https://wordlists.assetnote.io
- Focus on API endpoints and modern CMS paths

### PayloadsAllTheThings

Comprehensive collection of payloads and bypass techniques.

- GitHub: https://github.com/swisskyrepo/PayloadsAllTheThings

### FuzzDB

Collection of attack payloads and discovery wordlists.

- GitHub: https://github.com/fuzzdb-project/fuzzdb

## Combined Wordlists

You can merge multiple wordlists into one for broader coverage:

```bash
cat wordlists/default.txt wordlists/my_custom.txt wordlists/seclists_common.txt | sort -u > wordlists/combined.txt
```

Then use it:

```bash
python3 adminhunter.py https://target.com -w wordlists/combined.txt
```

## Performance Tips

- Smaller wordlists (under 1000 entries) finish in seconds
- Larger wordlists (10000+ entries) may take several minutes
- Use the `-t` flag to increase threads for faster scanning
- Use `--delay` to add a delay between requests if the target has rate limiting
- Use `--only-login` to filter results and reduce noise

## Legal Notice

All wordlists in this directory and any downloaded wordlists should only be used against systems you own or have explicit written permission to test. Unauthorized scanning is illegal in most jurisdictions.

## License

Wordlists included in this directory are provided for educational and authorized security testing purposes only.
