import json

def safe_json_loads(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Common fixes
        repaired = (
            text
            .replace("“", "\"")
            .replace("”", "\"")
            .replace("’", "'")
        )

        # Trim anything before first { and after last }
        start = repaired.find("{")
        end = repaired.rfind("}")
        if start != -1 and end != -1:
            repaired = repaired[start:end+1]

        return json.loads(repaired)
