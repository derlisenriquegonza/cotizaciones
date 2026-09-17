import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Ensure root folder is in sys.path for adapters import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from adapters.bonanza import BonanzaAdapter
from adapters.chaco import ChacoAdapter
from adapters.alberdi import AlberdiAdapter
from adapters.lamoneda import LaMonedaAdapter

adapters = [
    ("Bonanza", BonanzaAdapter.fetch),
    ("Cambios Chaco", ChacoAdapter.fetch),
    ("Cambios Alberdi", AlberdiAdapter.fetch),
    ("La Moneda", LaMonedaAdapter.fetch)
]

def fetch_single(adapter_tuple):
    name, fetch_fn = adapter_tuple
    try:
        return fetch_fn()
    except Exception as e:
        return {
            "source": name,
            "branch": "Desconocida",
            "usd_pyg": {"buy": None, "sell": None},
            "brl_pyg": {"buy": None, "sell": None},
            "usd_brl": {"buy": None, "sell": None},
            "sourceUpdatedAt": None,
            "retrievedAt": None,
            "status": "error",
            "error": f"Error inesperado: {str(e)}"
        }

def handler(event, context):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fetch_single, adapters))
        
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
        },
        "body": json.dumps(results, ensure_ascii=False)
    }
