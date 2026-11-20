"""Demo shop (the 'customer app'). It has a few real bugs on purpose. Every unhandled error is reported
to the Bug Agent dashboard, which starts investigating automatically."""
import collections
import hmac
import json
import os
import secrets
import threading
import time
import traceback
import urllib.request
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from app.auth import login
from app.cart import apply_coupon
from app.catalog import cheapest_in_category
from app.orders import average_item_price
from app.profile import display_name
from app.shipping import shipping_cost

ROOT = Path(__file__).resolve().parent
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://127.0.0.1:8000")
AUTOFIX_TOKEN = os.environ.get("AUTOFIX_TOKEN", "")
# Local runs PUSH errors to the dashboard. On a host the dashboard cannot reach (e.g. Render, with the dashboard on
# your laptop) set AUTOFIX_TOKEN: errors then wait in an outbox and the dashboard PULLS them using that token.
PUSH = os.environ.get("AUTOFIX_PUSH", "0" if AUTOFIX_TOKEN else "1") == "1"
BOOT_ID = secrets.token_hex(4)          # changes whenever this process restarts (the outbox starts over)
_outbox = collections.deque(maxlen=200)
_outbox_lock = threading.Lock()
_seq = 0
app = Flask(__name__)


def _redact(obj):
    if isinstance(obj, dict):
        return {k: ("***" if any(w in k.lower() for w in ("pass", "token", "secret")) else _redact(v))
                for k, v in obj.items()}
    return obj


def report_error(exc: Exception):
    if request.headers.get("X-Autofix-Replay"):  # the dashboard replaying a failing request must not raise a new incident
        return
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    tb = tb.replace(str(ROOT) + os.sep, "").replace(str(ROOT) + "/", "")
    payload = {
        "app": "acme-shop",
        "error_type": type(exc).__name__,
        "message": str(exc),
        "traceback": tb,
        "method": request.method,
        "path": request.path,
        "request_body": _redact(request.get_json(silent=True) or {}),
    }

    global _seq
    with _outbox_lock:
        _seq += 1
        _outbox.append({"seq": _seq, "ts": time.time(), **payload})
    if not PUSH:
        return

    def send():
        try:
            req = urllib.request.Request(DASHBOARD_URL + "/api/errors", data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=3).read()
        except Exception as e:  # the dashboard being down must never break the app
            print(f"[error-reporter] could not reach dashboard: {e}")

    threading.Thread(target=send, daemon=True).start()


@app.errorhandler(Exception)
def on_error(exc):
    if isinstance(exc, HTTPException):  # 404 (favicon, typos), 405, 400... are not bugs; only 5xx are reported
        if exc.code >= 500:
            report_error(exc)
        return jsonify(error=exc.name), exc.code
    report_error(exc)
    return jsonify(error="internal server error"), 500


@app.get("/healthz")
def healthz():
    return "ok"


@app.get("/_autofix/errors")
def autofix_errors():
    """The dashboard pulls new errors from here. Disabled unless AUTOFIX_TOKEN is set."""
    if not AUTOFIX_TOKEN:
        return jsonify(error="Not Found"), 404
    if not hmac.compare_digest(request.headers.get("X-Autofix-Token", "").encode(), AUTOFIX_TOKEN.encode()):
        return jsonify(error="forbidden"), 403
    after = request.args.get("after", type=int, default=0)
    with _outbox_lock:
        errors = [e for e in _outbox if e["seq"] > after]
    return jsonify(boot=BOOT_ID, errors=errors)


@app.post("/api/login")
def api_login():
    d = request.get_json(force=True)
    r = login(d.get("email", ""), d.get("password", ""))
    return jsonify(r), r["status"]


@app.post("/api/coupon")
def api_coupon():
    d = request.get_json(force=True)
    r = apply_coupon(float(d.get("total", 0)), d.get("code", ""))
    return jsonify(r), r["status"]


@app.post("/api/cart/average")
def api_average():
    d = request.get_json(force=True)
    return jsonify(average=average_item_price(d.get("prices", [])))


@app.post("/api/shipping")
def api_shipping():
    d = request.get_json(force=True)
    r = shipping_cost(float(d.get("weight", 0)))
    return jsonify(r), r["status"]


@app.post("/api/profile/name")
def api_profile_name():
    d = request.get_json(force=True)
    return jsonify(name=display_name(d.get("first", ""), d.get("middle"), d.get("last", "")))


@app.post("/api/catalog/cheapest")
def api_cheapest():
    d = request.get_json(force=True)
    return jsonify(product=cheapest_in_category(d.get("category", "")))


LAYOUT = """<!doctype html><html><head><meta charset="utf-8"><title>Acme Shop</title>
<style>
body{font-family:system-ui,sans-serif;background:#f5f6f8;margin:0;color:#1b1f24}
header{background:#1b1f24;color:#fff;padding:16px 28px;font-weight:600;font-size:18px}
main{max-width:820px;margin:28px auto;padding:0 18px;display:grid;gap:18px}
.card{background:#fff;border-radius:10px;padding:20px;box-shadow:0 1px 3px #0001}
h2{margin:0 0 12px;font-size:16px}
input{padding:9px 11px;border:1px solid #ccd;border-radius:6px;margin:0 8px 8px 0;font-size:14px}
button{padding:9px 16px;border:0;border-radius:6px;background:#2f6feb;color:#fff;font-size:14px;cursor:pointer}
.out{margin-top:10px;font-size:14px;padding:9px 11px;border-radius:6px;background:#eef1f5;min-height:18px}
.err{background:#fde8e8;color:#9b1c1c}.ok{background:#e3f6e8;color:#14532d}
small{color:#667}
nav{display:inline-flex;gap:18px;margin-left:36px;font-size:14px;font-weight:400}nav a{color:#cfd6e0;text-decoration:none}nav a:hover{color:#fff}
</style></head><body>
<header>Acme Shop<nav><a href="/">Home</a><a href="/checkout">Checkout</a><a href="/profile">Profile</a><a href="/catalog">Catalog</a></nav></header><main>
<!--BODY-->
</main><script>
async function send(url,body,out,fmt){
  const el=document.getElementById(out);el.className='out';el.textContent='...';
  try{const res=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const r=await res.json();
  if(res.ok){el.className='out ok';el.textContent=fmt(r)}
  else{el.className='out err';el.textContent=res.status==500?'Something went wrong (500). The error was reported to the Bug Agent.':(r.error||'Error '+res.status)}
  }catch(e){el.className='out err';el.textContent='Network error'}}
</script></body></html>"""


@app.get("/favicon.ico")
def favicon():
    return "", 204


def render(body: str) -> str:
    return LAYOUT.replace("<!--BODY-->", body)


HOME = """<div class="card"><h2>Sign in</h2><small>demo user: alice@example.com / secret123</small><br><br>
<input id="email" placeholder="email" value="Alice@Example.com"><input id="pw" type="password" placeholder="password" value="secret123">
<button onclick="send('/api/login',{email:email.value,password:pw.value},'o1',r=>'Signed in, token '+r.token)">Sign in</button>
<div id="o1" class="out"></div></div>
<div class="card"><h2>Apply coupon</h2><small>valid codes: SAVE10, SAVE20</small><br><br>
<input id="total" value="100" size="6"><input id="code" value="WELCOME50" size="12">
<button onclick="send('/api/coupon',{total:total.value,code:code.value},'o2',r=>'New total: '+r.total)">Apply coupon</button>
<div id="o2" class="out"></div></div>
<div class="card"><h2>Cart summary</h2><small>your cart is empty</small><br><br>
<button onclick="send('/api/cart/average',{prices:[]},'o3',r=>'Average item price: '+r.average)">Show average item price</button>
<div id="o3" class="out"></div></div>
"""

CHECKOUT = """<div class="card"><h2>Shipping estimate</h2><small>bands: up to 1 kg, 5 kg, 20 kg</small><br><br>
<input id="weight" value="25" size="6"> kg
<button onclick="send('/api/shipping',{weight:weight.value},'o4',r=>'Shipping: '+r.cost+' (band up to '+r.band_kg+' kg)')">Get shipping cost</button>
<div id="o4" class="out"></div></div>"""

PROFILE = """<div class="card"><h2>Display name</h2><small>leave the middle name empty if you have none</small><br><br>
<input id="first" value="Ravi" size="10"><input id="middle" placeholder="middle" size="10"><input id="last" value="Kumar" size="10">
<button onclick="send('/api/profile/name',{first:first.value,middle:middle.value||null,last:last.value},'o5',r=>'Shown as: '+r.name)">Preview name</button>
<div id="o5" class="out"></div></div>"""

CATALOG = """<div class="card"><h2>Cheapest in category</h2><small>categories: books, kitchen, electronics, toys</small><br><br>
<input id="cat" value="toys" size="14">
<button onclick="send('/api/catalog/cheapest',{category:cat.value},'o6',r=>r.product.name+' ('+r.product.price+')')">Find cheapest</button>
<div id="o6" class="out"></div></div>"""


@app.get("/")
def index():
    return render(HOME)


@app.get("/checkout")
def checkout():
    return render(CHECKOUT)


@app.get("/profile")
def profile():
    return render(PROFILE)


@app.get("/catalog")
def catalog():
    return render(CATALOG)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, use_reloader=True)
