import urllib.request
import ssl
import json
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

class ChacoAdapter:
    @staticmethod
    def fetch():
        url = "https://www.cambioschaco.com.py/api/branch_office/9/exchange_rates"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*'
        }
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        now_str = datetime.now().astimezone().isoformat()

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            
            items = data.get("items", [])
            usd_item = next((i for i in items if i.get("isoCode") == "USD"), {})
            brl_item = next((i for i in items if i.get("isoCode") == "BRL"), {})

            usd_pyg = {"buy": clean_num(usd_item.get("purchasePrice")), "sell": clean_num(usd_item.get("salePrice"))}
            brl_pyg = {"buy": clean_num(brl_item.get("purchasePrice")), "sell": clean_num(brl_item.get("salePrice"))}
            usd_brl = {"buy": clean_num(brl_item.get("purchaseArbitrage")), "sell": clean_num(brl_item.get("saleArbitrage"))}

            source_updated_at = data.get("updateTs")

            return {
                "source": "Cambios Chaco",
                "branch": "Sucursal Adrián Jara",
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
                "source": "Cambios Chaco",
                "branch": "Sucursal Adrián Jara",
                "usd_pyg": {"buy": None, "sell": None},
                "brl_pyg": {"buy": None, "sell": None},
                "usd_brl": {"buy": None, "sell": None},
                "sourceUpdatedAt": None,
                "retrievedAt": now_str,
                "status": "error",
                "error": f"No fue posible obtener la cotización: {str(e)}"
            }
