import urllib.request
import ssl
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

class AlberdiAdapter:
    @staticmethod
    def fetch():
        url = "https://www.cambiosalberdi.com/langes/index.php?suc=ciudaddeleste"
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

            def get_row_rates(keyword_pattern):
                m = re.search(r'<tr[^>]*>.*?<td[^>]*>.*?(?:'+keyword_pattern+r').*?</td>\s*<td[^>]*>\s*([\d.,]+)\s*</td>\s*<td[^>]*>\s*([\d.,]+)\s*</td>.*?</tr>', html, re.IGNORECASE | re.DOTALL)
                if not m:
                    return {"buy": None, "sell": None}
                return {"buy": clean_num(m.group(1)), "sell": clean_num(m.group(2))}

            usd_pyg = get_row_rates(r'D&oacute;lar Americano|Dólar Americano')
            brl_pyg = get_row_rates(r'Real Brasile&ntilde;o|Real Brasileño')
            usd_brl = get_row_rates(r'D&oacute;lar Americano x Real|Dólar Americano x Real')

            ts_match = re.search(r'class="update-status">\s*(?:&Uacute;|Ú)ltima actualizaci(?:&oacute;|ó)n\s*([^<]+)', html, re.IGNORECASE)
            source_updated_at = ts_match.group(1).strip() if ts_match else None

            return {
                "source": "Cambios Alberdi",
                "branch": "Ciudad del Este",
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
                "source": "Cambios Alberdi",
                "branch": "Ciudad del Este",
                "usd_pyg": {"buy": None, "sell": None},
                "brl_pyg": {"buy": None, "sell": None},
                "usd_brl": {"buy": None, "sell": None},
                "sourceUpdatedAt": None,
                "retrievedAt": now_str,
                "status": "error",
                "error": f"No fue posible obtener la cotización: {str(e)}"
            }
