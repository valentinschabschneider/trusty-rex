from pydantic.alias_generators import to_camel


def too_camel(s: str):
    if "[" in s:
        return s
    return to_camel(s)


def camelize_diff(d):
    if isinstance(d, list):
        return [camelize_diff(i) if isinstance(i, (dict, list)) else i for i in d]
    return {
        too_camel(a): camelize_diff(b) if isinstance(b, (dict, list)) else b
        for a, b in d.items()
    }
