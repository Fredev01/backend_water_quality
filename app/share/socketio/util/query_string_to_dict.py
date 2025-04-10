from urllib.parse import parse_qs


def query_string_to_dict(query_string: str) -> dict:
    parsed = parse_qs(query_string)

    return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
