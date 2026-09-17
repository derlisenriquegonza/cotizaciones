import os
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, send_from_directory
from adapters.bonanza import BonanzaAdapter
from adapters.chaco import ChacoAdapter
from adapters.alberdi import AlberdiAdapter
from adapters.lamoneda import LaMonedaAdapter

app = Flask(__name__, static_folder=".")

# Suppress trailing slash redirection issues
app.url_map.strict_slashes = False

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

@app.route("/api/rates", methods=["GET"])
def get_rates():
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fetch_single, adapters))
    
    # Add CORS headers explicitly
    response = jsonify(results)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Server starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
