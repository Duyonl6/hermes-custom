import json, hashlib, asyncio
import numpy as np

try:
    from redis import asyncio as aioredis
    from sentence_transformers import SentenceTransformer
    _embedder  = SentenceTransformer('all-MiniLM-L6-v2')
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

_redis    = None
THRESHOLD = 0.85
TTL       = 3600

async def _r():
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url("redis://localhost:6379")
    return _redis

def _embed(t):
    return _embedder.encode(t, normalize_embeddings=True)

async def cache_get(query):
    if not _AVAILABLE: return None
    try:
        r, qv = await _r(), _embed(query)
        keys  = await r.keys("hcache:*")
        best_sim, best_resp = 0.0, None
        for k in keys:
            raw = await r.get(k)
            if not raw: continue
            e   = json.loads(raw)
            sim = float(np.dot(qv, np.array(e["emb"])))
            if sim > best_sim: best_sim, best_resp = sim, e["resp"]
        if best_sim >= THRESHOLD:
            print(f"[cache] HIT sim={best_sim:.3f}")
            return best_resp
    except Exception as e: print(f"[cache] ERROR: {e}")
    return None

async def cache_set(query, response):
    if not _AVAILABLE: return
    try:
        r   = await _r()
        key = f"hcache:{hashlib.md5(query.encode()).hexdigest()}"
        await r.setex(key, TTL, json.dumps({
            "emb":  _embed(query).tolist(),
            "resp": response
        }))
        print(f"[cache] SAVED '{query[:60]}'")
    except Exception as e: print(f"[cache] ERROR: {e}")

async def cache_stats():
    if not _AVAILABLE: return {"available": False}
    try:
        r = await _r()
        return {"available": True, "entries": len(await r.keys("hcache:*")), "ttl": TTL}
    except Exception as e: return {"error": str(e)}

if __name__ == "__main__":
    async def _test():
        print("=== Cache Test ===")
        await cache_set("Docker là gì?", "Docker là nền tảng container hóa.")
        r1 = await cache_get("Docker là gì?")
        print("Exact match:  ", "✅ HIT" if r1 else "❌ MISS")
        r2 = await cache_get("Giải thích Docker cho tôi")
        print("Similar query:", "✅ HIT" if r2 else "⚠️  MISS (bình thường)")
        print("Stats:", await cache_stats())
    asyncio.run(_test())
