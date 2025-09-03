import json
import re
from enum import Enum
from typing import Any

from deepdiff import DeepDiff, DeepHash

from app.api.routes.schemas import RecordStateDiff
from app.models import RecordStateBase


class DiffNotation(str, Enum):
    python = "python"
    dot = "dot"


def generate_diff_any(base: Any, other: Any):
    return DeepDiff(base, other)


def generate_diff(
    base_record_state: RecordStateDiff,
    other_record_state: RecordStateDiff,
    notation: DiffNotation = DiffNotation.python,
):
    return deep_diff_to_dict(
        generate_diff_any(base_record_state.data, other_record_state.data), notation
    )


def generate_diffs(
    record_states: list[RecordStateBase], notation: DiffNotation = DiffNotation.python
) -> list[RecordStateDiff]:
    diff_pairs = [
        (
            record_states[i],
            (
                {}
                if i == 0
                else generate_diff(record_states[i - 1], record_states[i], notation)
            ),
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


def deep_diff_to_dict(diff: DeepDiff, notation: DiffNotation = DiffNotation.python):
    # diff.to_dict() has some weird types
    diff_dict = json.loads(diff.to_json())

    if "values_changed" in diff_dict:
        diff_dict["values_changed"] = list(diff_dict["values_changed"].keys())

    if "iterable_item_added" in diff_dict:
        diff_dict["iterable_item_added"] = list(diff_dict["iterable_item_added"].keys())

    if "iterable_item_removed" in diff_dict:
        diff_dict["iterable_item_removed"] = list(
            diff_dict["iterable_item_removed"].keys()
        )

    if "dictionary_item_added" in diff_dict:
        diff_dict["dictionary_item_added"] = list(
            diff_dict["dictionary_item_added"].keys()
        )

    if "dictionary_item_removed" in diff_dict:
        diff_dict["dictionary_item_removed"] = list(
            diff_dict["dictionary_item_removed"].keys()
        )

    if notation == DiffNotation.dot:
        if "values_changed" in diff_dict:
            diff_dict["values_changed"] = convert_list_keys(diff_dict["values_changed"])
        if "iterable_item_added" in diff_dict:
            diff_dict["iterable_item_added"] = convert_list_keys(
                diff_dict["iterable_item_added"]
            )
        if "iterable_item_removed" in diff_dict:
            diff_dict["iterable_item_removed"] = convert_list_keys(
                diff_dict["iterable_item_removed"]
            )
        if "dictionary_item_added" in diff_dict:
            diff_dict["dictionary_item_added"] = convert_list_keys(
                diff_dict["dictionary_item_added"]
            )
        if "dictionary_item_removed" in diff_dict:
            diff_dict["dictionary_item_removed"] = convert_list_keys(
                diff_dict["dictionary_item_removed"]
            )

    return diff_dict


def convert_diff_path_to_dot_notation(path):
    # Replace ['key'] with .key
    path = re.sub(r"\['([^']+)'\]", r".\1", path)
    # Ensure the path does not start with a dot
    if path.startswith("."):
        path = path[1:]
    # Remove 'root.' if it's at the start
    if path.startswith("root."):
        path = path[5:]
    return path


# def convert_dict_keys(d):
#     # Create a new dictionary with converted keys
#     new_dict = {}
#     for key, value in d.items():
#         new_key = convert_diff_path_to_dot_notation(key)
#         new_dict[new_key] = value
#     return new_dict


def convert_list_keys(l):
    # Create a new list with converted keys
    new_list = []
    for item in l:
        new_list.append(convert_diff_path_to_dot_notation(item))
    return new_list
