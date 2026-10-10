import socket, ssl, time, secrets, string, ipaddress, re
from urllib.parse import urlparse
import requests, dns.resolver, dns.exception
from config import HTTP_TIMEOUT, USER_AGENT, MAX_URL_LEN, MAX_INPUT_LEN
def _validate_input(text, max_len=MAX_INPUT_LEN):
    if not text: return None
    text = text.strip()
    return None if len(text) > max_len else text
def _normalize_url(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")): url = "https://" + url
    return url
def validate_url(url):
    url = _validate_input(url, MAX_URL_LEN)
    if not url: return (False, "❌ المدخل فارغ.", None)
    try:
        u = _normalize_url(url); p = urlparse(u)
        if p.scheme not in ("http", "https"): return (False, "❌ المخطط.", None)
        if not p.netloc: return (False, "❌ لا نطاق.", None)
        if not p.hostname or "." not in p.hostname: return (False, "❌ نطاق غير صالح.", None)
        return (True, "✅ صالح.", u)
    except Exception as e: return (False, f"❌ {e}", None)
def extract_domain(url):
    try:
        u = _normalize_url(url); host = urlparse(u).hostname
        if not host: return (False, "❌ لا نطاق.", None)
        return (True, f"🌐 <b>{host}</b>", host)
    except Exception as e: return (False, f"❌ {e}", None)
def dns_lookup(domain, rtype="A"):
    domain = _validate_input(domain, MAX_URL_LEN)
    if not domain: return (False, "❌ مدخل.", [])
    if domain.startswith(("http://", "https://")): domain = urlparse(domain).hostname
    try:
        ans = dns.resolver.resolve(domain, rtype, lifetime=HTTP_TIMEOUT)
        return (True, f"✅ {rtype}:", [r.to_text() for r in ans])
    except dns.resolver.NXDOMAIN: return (False, "❌ غير موجود.", [])
    except dns.resolver.NoAnswer: return (False, f"❌ لا {rtype}.", [])
    except dns.exception.Timeout: return (False, "❌ مهلة.", [])
    except Exception as e: return (False, f"❌ {e}", [])
def all_dns_records(domain):
    out = {}
    for rt in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        ok, _, r = dns_lookup(domain, rt)
        if ok: out[rt] = r
    return out
def resolve_ip(domain):
    try:
        domain = _validate_input(domain, MAX_URL_LEN)
        if not domain: return (False, "❌ مدخل.", None)
        if domain.startswith(("http://", "https://")): domain = urlparse(domain).hostname
        infos = socket.getaddrinfo(domain, None)
        ips = sorted({i[4][0] for i in infos})
        return (True, "✅ IP:", ips) if ips else (False, "❌ لا IP.", None)
    except Exception as e: return (False, f"❌ {e}", None)
def check_response(url):
    ok, msg, norm = validate_url(url)
    if not ok: return (False, msg, None)
    try:
        t0 = time.time()
        r = requests.get(norm, timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
        el = time.time() - t0
        info = {"status": r.status_code, "final_url": r.url, "elapsed": round(el, 3), "size": len(r.content)}
        text = f"✅ HTTP: {info['status']}\n⏱️ {info['elapsed']}s\n📦 {info['size']}"
        return (True, text, info)
    except Exception as e: return (False, f"❌ {e}", None)
def check_ssl(domain):
    try:
        domain = _validate_input(domain, MAX_URL_LEN)
        if not domain: return (False, "❌ مدخل.", None)
        if domain.startswith(("http://", "https://")): domain = urlparse(domain).hostname
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=HTTP_TIMEOUT) as s:
            with ctx.wrap_socket(s, server_hostname=domain) as ss:
                cert = ss.getpeercert()
                subj = dict(x[0] for x in cert.get("subject", []))
                info = {"subject": subj.get("commonName", "—"), "not_before": cert.get("notBefore", "—"), "not_after": cert.get("notAfter", "—")}
                text = f"🔒 {info['subject']}\n📅 {info['not_before']}\n📅 {info['not_after']}"
                return (True, text, info)
    except Exception as e: return (False, f"❌ {e}", None)
def check_security_headers(url):
    ok, msg, norm = validate_url(url)
    if not ok: return (False, msg, None)
    try:
        r = requests.get(norm, timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT})
        h = {k.lower(): v for k, v in r.headers.items()}
        checks = {"strict-transport-security": "HSTS", "x-frame-options": "X-Frame", "x-content-type-options": "X-Content", "content-security-policy": "CSP"}
        lines = ["🔐 <b>ترويسات الأمان</b>"]; present = 0
        for k, n in checks.items():
            if k in h: lines.append(f"✅ {n}"); present += 1
            else: lines.append(f"❌ {n}")
        lines.append(f"\n📊 {present}/{len(checks)}")
        return (True, "\n".join(lines), {"present": present})
    except Exception as e: return (False, f"❌ {e}", None)
def analyze_ip(ip):
    ip = _validate_input(ip, 100)
    if not ip: return (False, "❌ مدخل.", None)
    try:
        a = ipaddress.ip_address(ip)
        lines = [f"🌐 {ip}", f"🔢 IPv{a.version}", f"🏠 خاص: {'نعم' if a.is_private else 'لا'}", f"🔄 Loopback: {'نعم' if a.is_loopback else 'لا'}"]
        return (True, "\n".join(lines), {"version": a.version})
    except ValueError: return (False, "❌ ليس IP.", None)
def check_tcp_port(host, port):
    try:
        host = _validate_input(host, 200); port = int(port)
        if not (1 <= port <= 65535): return (False, "❌ منفذ.", None)
        t0 = time.time()
        with socket.create_connection((host, port), timeout=HTTP_TIMEOUT):
            el = time.time() - t0
            return (True, f"✅ {host}:{port}\n⏱️ {round(el,3)}s", {"open": True})
    except socket.timeout: return (False, "⏱️ مغلق.", None)
    except ConnectionRefusedError: return (False, "🚫 مغلق.", None)
    except Exception as e: return (False, f"❌ {e}", None)
def generate_password(length=16):
    try:
        length = int(length)
        if not (8 <= length <= 128): return (False, "❌ 8-128.", None)
        pool = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*()-_=+"
        pwd = "".join(secrets.choice(pool) for _ in range(length))
        return (True, f"🔐 <code>{pwd}</code>\n📏 {length}", pwd)
    except Exception as e: return (False, f"❌ {e}", None)
def check_password_strength(password):
    if not password: return (False, "❌ فارغة.", None)
    ln = len(password); score = 0
    if ln >= 8: score += 1
    if ln >= 12: score += 1
    if ln >= 16: score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"\d", password): score += 1
    if re.search(r"[!@#$%^&*()_\-+=]", password): score += 1
    v = ("🔴 ضعيفة" if score <= 2 else "🟠 ضعيفة" if score <= 4 else "🟡 متوسطة" if score <= 6 else "🟢 قوية" if score <= 7 else "💚 قوية جداً")
    return (True, f"📏 {ln}\n🎯 {v}\n📈 {score}/8", {"score": score})
