import json

def safe_parse(output):
    try:
        data = json.loads(output)
    except:
        return {
            "title": "Parsing Failed",
            "summary": str(output),
            "methodology": "",
            "contributions": [],
            "results": "",
            "metrics": {}
        }

    # ✅ FIX NESTED STRUCTURE (YOUR MAIN BUG)
    if isinstance(data.get("summary"), dict):
        inner = data["summary"]
        return {
            "title": inner.get("title", ""),
            "summary": inner.get("summary", ""),
            "methodology": inner.get("methodology", ""),
            "contributions": inner.get("contributions", []),
            "results": inner.get("results", ""),
            "metrics": inner.get("metrics", {})
        }

    return data
