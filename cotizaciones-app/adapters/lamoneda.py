import urllib.request
import ssl
import json
import re
from datetime import datetime

def clean_num(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip().replace('.', '').replace(',', '.')
    try:
        return float(val_str)
    except ValueError:
        return None

class LaMonedaAdapter:
    @staticmethod
    def fetch():
        url = "https://www.lamoneda.com.py/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        now_str = datetime.now().astimezone().isoformat()

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            usd_pyg = {"buy": None, "sell": None}
            brl_pyg = {"buy": None, "sell": None}
            usd_brl = {"buy": None, "sell": None}

            db_match = re.search(r'LM_TASAS_DB\s*=\s*(\{.*?\});', html, re.DOTALL)
            if db_match:
                db = json.loads(db_match.group(1))
                usd = db.get("USD", {})
                brl = db.get("BRL", {})
                usd_brl_db = db.get("USD-BRL", {})

                usd_pyg = {"buy": clean_num(usd.get("compra")), "sell": clean_num(usd.get("venta"))}
                brl_pyg = {"buy": clean_num(brl.get("compra")), "sell": clean_num(brl.get("venta"))}
                usd_brl = {"buy": clean_num(usd_brl_db.get("compra")), "sell": clean_num(usd_brl_db.get("venta"))}

            ts_match = re.search(r'id=["\'](?:mobile)?lastUpdateDisplay["\'][^>]*>([^<]+)<', html, re.IGNORECASE)
            source_updated_at = ts_match.group(1).strip() if ts_match else None

            return {
                "source": "La Moneda",
                "branch": "Casa Matriz",
                "usd_pyg": usd_pyg,
                "brl_pyg": brl_pyg,
                "usd_brl": usd_brl,
                "sourceUpdatedAt": source_updated_at,
                "retrievedAt": now_str,
                "status": "ok",
                "error": None
            }
        except Exception as e:
            return {
                "source": "La Moneda",
                "branch": "Casa Matriz",
                "usd_pyg": {"buy": None, "sell": None},
                "brl_pyg": {"buy": None, "sell": None},
                "usd_brl": {"buy": None, "sell": None},
                "sourceUpdatedAt": None,
                "retrievedAt": now_str,
                "status": "error",
                "error": f"No fue posible obtener la cotización: {str(e)}"
            }
