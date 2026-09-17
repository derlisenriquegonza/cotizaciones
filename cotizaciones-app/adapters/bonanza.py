import urllib.request
import ssl
import re
from datetime import datetime, timezone

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

class BonanzaAdapter:
    @staticmethod
    def fetch():
        url = "https://www.bonanzacambios.com.py/"
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
            
            # Extract section for Casa Matriz (tab-0 MATRIZ)
            matriz_match = re.search(r'<!--\s*/\.tab-0 MATRIZ\s*-->(.*?)<!--\s*/\.tab-1', html, re.DOTALL)
            content = matriz_match.group(1) if matriz_match else html

            def get_row_rates(pattern, text):
                m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if not m:
                    return {"buy": None, "sell": None}
                row_html = m.group(1)
                vals = re.findall(r'<td class="moneda">\s*([\d.,]+)\s*</td>', row_html)
                buy = clean_num(vals[0]) if len(vals) > 0 else None
                sell = clean_num(vals[1]) if len(vals) > 1 else None
                return {"buy": buy, "sell": sell}

            usd_pyg = get_row_rates(r'<td class="title">\s*Dolar Americano\s*</td>(.*?)</tr>', content)
            brl_pyg = get_row_rates(r'<td class="title">\s*Real\s*</td>(.*?)</tr>', content)
            usd_brl = get_row_rates(r'<td class="title">\s*Dolar Americano x Real\s*</td>(.*?)</tr>', content)

            ts_match = re.search(r'actualizado el ([^<]+)', content)
            source_updated_at = ts_match.group(1).strip() if ts_match else None

            return {
                "source": "Bonanza",
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
                "source": "Bonanza",
                "branch": "Casa Matriz",
                "usd_pyg": {"buy": None, "sell": None},
                "brl_pyg": {"buy": None, "sell": None},
                "usd_brl": {"buy": None, "sell": None},
                "sourceUpdatedAt": None,
                "retrievedAt": now_str,
                "status": "error",
                "error": f"No fue posible obtener la cotización: {str(e)}"
            }
