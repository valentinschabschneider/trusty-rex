from typing import Any

from deepdiff import DeepDiff, DeepHash

from app.api.routes.schemas import RecordStateDiff


def generate_diff_any(base: Any, other: Any):
    return DeepDiff(base, other)


def generate_diff(
    base_record_state: RecordStateDiff, other_record_state: RecordStateDiff
):
    return generate_diff_any(base_record_state.data, other_record_state.data)


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
