from deepdiff import DeepDiff, DeepHash

from app.api.routes.schemas import RecordStateDiff

# def too_camel(s: str):
#     if "[" in s:
#         return s
#     return to_camel(s)


# def camelize_dict_keys(d):
#     if isinstance(d, list):
#         return [camelize_dict_keys(i) if isinstance(i, (dict, list)) else i for i in d]
#     return {
#         too_camel(a): camelize_dict_keys(b) if isinstance(b, (dict, list)) else b
#         for a, b in d.items()
#     }


def generate_diff(
    base_record_state: RecordStateDiff, other_record_state: RecordStateDiff
):
    print(DeepDiff(base_record_state.data, other_record_state.data).to_dict())

    return DeepDiff(base_record_state.data, other_record_state.data)


def generate_diffs(record_states: list[RecordStateDiff]) -> list[RecordStateDiff]:
    diff_pairs = [
        (
            record_states[i],
            ({} if i == 0 else generate_diff(record_states[i - 1], record_states[i])),
        )
        for i in range(0, len(record_states))
    ]

    return [
        RecordStateDiff(
            id=pair[0].id,
            key=pair[0].key,
            data=pair[0].data,
            meta=pair[0].meta,
            created_at=pair[0].created_at,
            diff_to_previous=pair[1] if pair[1] != {} else None,
            hash=DeepHash(pair[0].data)[pair[0].data],
        )
        for pair in diff_pairs
    ]
