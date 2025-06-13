
import json
import requests
import time
import threading
from flask import Flask, jsonify

app = Flask(__name__)
CACHE_FILE = "tokens_cache.json"
RPC_URL = "https://api.mainnet-beta.solana.com"

tokens = []
seen_signatures = set()

def save_tokens():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

def get_signatures(limit=50):
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            {"limit": limit}
        ]
    }
    try:
        res = requests.post(RPC_URL, json=body, timeout=10)
        return [tx["signature"] for tx in res.json().get("result", [])]
    except Exception as e:
        print("Ошибка getSignatures:", e)
        return []

def get_transaction(sig):
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [sig, {"encoding": "jsonParsed"}]
    }
    try:
        res = requests.post(RPC_URL, json=body, timeout=10)
        return res.json().get("result")
    except Exception as e:
        print("Ошибка getTransaction:", e)
        return None

def extract_token_info(tx):
    found = []
    if not tx:
        return found
    instructions = tx.get("transaction", {}).get("message", {}).get("instructions", [])
    for ix in instructions:
        if ix.get("program") == "spl-token":
            print("➡️ Инструкция:", ix.get("parsed", {}))
        if ix.get("program") == "spl-token" and ix.get("parsed", {}).get("type") == "initializeMint":
            info = ix["parsed"]["info"]
            found.append({
                "mint": ix.get("accounts", [None])[0],
                "decimals": info.get("decimals"),
                "mintAuthority": info.get("mintAuthority"),
                "freezeAuthority": info.get("freezeAuthority")
            })
    return found

def polling_loop():
    global tokens
    print("📡 Polling активирован...")

    while True:
        sigs = get_signatures(limit=50)
        for sig in sigs:
            if sig in seen_signatures:
                continue
            seen_signatures.add(sig)
            print("🔍 Проверяем сигнатуру:", sig)

            tx = get_transaction(sig)
            print("📦 Транзакция:", "OK" if tx else "None")

            new_tokens = extract_token_info(tx)

            for token in new_tokens:
                if token not in tokens:
                    tokens.append(token)
                    print("🪙 Новый токен:", token)
                    save_tokens()

            time.sleep(0.3)

        time.sleep(10)

@app.route("/tokens")
def get_tokens():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

if __name__ == "__main__":
    threading.Thread(target=polling_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
