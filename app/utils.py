from deepdiff import DeepDiff
from pydantic.alias_generators import to_camel

from app.database.models import RecordState as RecordStateModel


def too_camel(s: str):
    if "[" in s:
        return s
    return to_camel(s)


def camelize_dict_keys(d):
    if isinstance(d, list):
        return [camelize_dict_keys(i) if isinstance(i, (dict, list)) else i for i in d]
    return {
        too_camel(a): camelize_dict_keys(b) if isinstance(b, (dict, list)) else b
        for a, b in d.items()
    }


def generate_diffs(record_states: list[RecordStateModel]):
    diff_pairs = [
        (
            record_states[i],
            {}
            if i == 0
            else DeepDiff(record_states[i - 1].data, record_states[i].data),
        )
        for i in range(0, len(record_states))
    ]

    return [
        {
            "id": pair[0].id,
            "key": pair[0].key,
            "data": pair[0].data,
            "tags": pair[0].tags,
            "meta": pair[0].meta,
            "created": pair[0].created,
            "last_updated": pair[0].last_updated,
            "diff_to_previous": pair[1],
        }
        for pair in diff_pairs
    ]
