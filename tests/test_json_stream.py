# SPDX-FileCopyrightText: 2025 Justin Myers
#
# SPDX-License-Identifier: Unlicense

import json
import math

import pytest

import adafruit_json_stream

# ---------------
# Helpers
# ---------------


class BytesChunkIO:
    def __init__(self, data=b"", chunk_size=10):
        self.chunk_size = chunk_size
        self.chunks_read = 0
        self.data = data
        self.data_len = len(self.data)
        self.position = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.position > self.data_len:
            raise StopIteration

        end = self.chunk_size
        if self.position + end > self.data_len:
            end = self.data_len
        chunk = self.data[self.position : self.position + self.chunk_size]

        self.chunks_read += 1
        self.position += self.chunk_size

        return chunk

    def get_chunks_read(self):
        return self.chunks_read


# ---------------
# Fixtures
# ---------------


@pytest.fixture
def dict_with_all_types():
    return """
    {
        "_check": "{\\\"a\\\": 1, \\\"b\\\": [2,3]}",
        "bool": true,
        "dict": {"key": "value"},
        "float": 1.1,
        "int": 1,
        "list": [1,2,3],
        "null": null,
        "string": "string"
    }
    """


@pytest.fixture
def list_with_bad_strings():
    return r"""
    [
        "\"}\"",
        "{\"a\": 1, \"b\": [2,3]}",
        "\"",
        "\\\"",
        "\\\\\"",
        "\\x40\"",
        "[[[{{{",
        "]]]}}}"
    ]
    """


@pytest.fixture
def dict_with_bad_strings():
    return r"""
    {
        "1": "\"}\"",
        "2": "{\"a\": 1, \"b\": [2,3]}",
        "3": "\"",
        "4": "\\\"",
        "5": "\\\\\"",
        "6": "\\x40\"",
        "7": "[[[{{{",
        "8": "]]]}}}"
    }
    """


@pytest.fixture
def list_with_values():
    return """
    [
        1,
        2,
        3
    ]
    """


@pytest.fixture
def dict_with_keys():
    return """
    {
        "field_1": 1,
        "field_2": 2,
        "field_3": 3
    }
    """


@pytest.fixture
def dict_with_list_with_single_entries():
    return """
    {
        "list_1": [
            {
                "dict_id": 1
            },
            {
                "dict_id": 2
            },
            {
                "dict_id": 3
            },
            {
                "dict_id": 4
            }
        ]
    }
    """


@pytest.fixture
def complex_dict():
    return """
    {
        "list_1": [
            {
                "dict_id": 1,
                "dict_name": "one",
                "sub_dict": {
                    "sub_dict_id": 1.1,
                    "sub_dict_name": "one point one"
                },
                "sub_list": [
                    "a",
                    "b",
                    "c"
                ]
            },
            {
                "dict_id": 2,
                "dict_name": "two",
                "sub_dict": {
                    "sub_dict_id": 2.1,
                    "sub_dict_name": "two point one"
                },
                "sub_list": [
                    "d",
                    "e",
                    "f"
                ]
            }
        ],
        "list_2": [
            {
                "dict_id": 3,
                "dict_name": "three",
                "sub_dict": {
                    "sub_dict_id": 3.1,
                    "sub_dict_name": "three point one"
                },
                "sub_list": [
                    "g",
                    "h",
                    "i"
                ]
            },
            {
                "dict_id": 4,
                "dict_name": "four",
                "sub_dict": {
                    "sub_dict_id": 4.1,
                    "sub_dict_name": "four point one"
                },
                "sub_list": [
                    "j",
                    "k",
                    "l"
                ]
            }
        ]
    }
    """


# ---------------
# Tests
# ---------------


def test_all_types(dict_with_all_types):
    """Test loading a simple dict all data types."""

    assert json.loads(dict_with_all_types)

    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_all_types.encode()))

    assert stream["bool"] is True
    assert stream["dict"]["key"] == "value"
    assert stream["float"] == 1.1
    assert stream["int"] == 1
    assert next(stream["list"]) == 1
    assert stream["null"] is None
    assert stream["string"] == "string"


def test_simple_dict_with_keys(dict_with_keys):
    """Test loading a simple dict with keys."""

    assert json.loads(dict_with_keys)

    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_keys.encode()))
    for i in range(1, 4):
        assert stream[f"field_{i}"] == i
    with pytest.raises(KeyError, match="field_4"):
        stream["field_4"]


def test_simple_dict_with_grabbing_key_twice_raises(dict_with_keys):
    """Test loading a simple dict with keys twice raises."""

    assert json.loads(dict_with_keys)

    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_keys.encode()))
    assert stream["field_1"] == 1
    with pytest.raises(KeyError, match="field_1"):
        stream["field_1"]


def test_simple_dict_with_keys_middle_key(dict_with_keys):
    """Test loading a simple dict and grabbing a key in the middle."""

    assert json.loads(dict_with_keys)

    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_keys.encode()))
    assert stream["field_2"] == 2


def test_simple_dict_with_keys_missing_key_raises(dict_with_keys):
    """Test loading a simple dict and grabbing a key that doesn't exist raises."""

    assert json.loads(dict_with_keys)

    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_keys.encode()))
    with pytest.raises(KeyError, match="field_4"):
        stream["field_4"]


def test_list_with_values(list_with_values):
    """Test loading a list and iterating over it."""

    assert json.loads(list_with_values)

    stream = adafruit_json_stream.load(BytesChunkIO(list_with_values.encode()))
    counter = 0
    for value in stream:
        counter += 1
        assert value == counter


def test_dict_with_list_of_single_entries(dict_with_list_with_single_entries):
    """Test loading an dict with a list of dicts with one entry each."""

    assert json.loads(dict_with_list_with_single_entries)

    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_list_with_single_entries.encode()))
    counter = 0
    for obj in stream["list_1"]:
        counter += 1
        assert obj["dict_id"] == counter
    assert counter == 4


def test_complex_dict(complex_dict):
    """Test loading a complex dict."""

    assert json.loads(complex_dict)

    dict_names = [
        "one",
        "two",
        "three",
        "four",
    ]

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))
    counter = 0
    sub_counter = 0
    for obj in stream["list_1"]:
        counter += 1
        assert obj["dict_id"] == counter
        assert obj["dict_name"] == dict_names[counter - 1]
        sub_dict = obj["sub_dict"]
        assert sub_dict["sub_dict_id"] == counter + 0.1
        assert sub_dict["sub_dict_name"] == f"{dict_names[counter-1]} point one"
        for item in obj["sub_list"]:
            sub_counter += 1
            assert item == chr(96 + sub_counter)

    assert counter == 2
    assert sub_counter == 6

    for obj in stream["list_2"]:
        counter += 1
        assert obj["dict_id"] == counter
        assert obj["dict_name"] == dict_names[counter - 1]
        sub_dict = obj["sub_dict"]
        assert sub_dict["sub_dict_id"] == counter + 0.1
        assert sub_dict["sub_dict_name"] == f"{dict_names[counter-1]} point one"
        for item in obj["sub_list"]:
            sub_counter += 1
            assert item == chr(96 + sub_counter)

    assert counter == 4
    assert sub_counter == 12


def test_bad_strings_in_list(list_with_bad_strings):
    """Test loading different strings that can confuse the parser."""

    bad_strings = [
        '"}"',
        '{"a": 1, "b": [2,3]}',
        '"',
        '\\"',
        '\\\\"',
        '\\x40"',
        "[[[{{{",
        "]]]}}}",
    ]

    assert json.loads(list_with_bad_strings)

    # get each separately
    stream = adafruit_json_stream.load(BytesChunkIO(list_with_bad_strings.encode()))
    for i, item in enumerate(stream):
        assert item == bad_strings[i]


def test_bad_strings_in_list_iter(list_with_bad_strings):
    """Test loading different strings that can confuse the parser."""

    bad_strings = [
        '"}"',
        '{"a": 1, "b": [2,3]}',
        '"',
        '\\"',
        '\\\\"',
        '\\x40"',
        "[[[{{{",
        "]]]}}}",
    ]

    assert json.loads(list_with_bad_strings)

    # get each separately
    stream = adafruit_json_stream.load(BytesChunkIO(list_with_bad_strings.encode()))
    for i, item in enumerate(stream):
        assert item == bad_strings[i]


def test_bad_strings_in_dict_as_object(dict_with_bad_strings):
    """Test loading different strings that can confuse the parser."""

    bad_strings = {
        "1": '"}"',
        "2": '{"a": 1, "b": [2,3]}',
        "3": '"',
        "4": '\\"',
        "5": '\\\\"',
        "6": '\\x40"',
        "7": "[[[{{{",
        "8": "]]]}}}",
    }

    # read all at once
    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_bad_strings.encode()))
    assert stream.as_object() == bad_strings


def test_bad_strings_in_dict_all_keys(dict_with_bad_strings):
    """Test loading different strings that can confuse the parser."""

    bad_strings = {
        "1": '"}"',
        "2": '{"a": 1, "b": [2,3]}',
        "3": '"',
        "4": '\\"',
        "5": '\\\\"',
        "6": '\\x40"',
        "7": "[[[{{{",
        "8": "]]]}}}",
    }

    # read one after the other with keys
    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_bad_strings.encode()))
    assert stream["1"] == bad_strings["1"]
    assert stream["2"] == bad_strings["2"]
    assert stream["3"] == bad_strings["3"]
    assert stream["4"] == bad_strings["4"]
    assert stream["5"] == bad_strings["5"]
    assert stream["6"] == bad_strings["6"]
    assert stream["7"] == bad_strings["7"]
    assert stream["8"] == bad_strings["8"]


def test_bad_strings_in_dict_skip_some(dict_with_bad_strings):
    """Test loading different strings that can confuse the parser."""

    bad_strings = {
        "1": '"}"',
        "2": '{"a": 1, "b": [2,3]}',
        "3": '"',
        "4": '\\"',
        "5": '\\\\"',
        "6": '\\x40"',
        "7": "[[[{{{",
        "8": "]]]}}}",
    }

    # read some, skip some
    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_bad_strings.encode()))
    assert stream["2"] == bad_strings["2"]
    assert stream["5"] == bad_strings["5"]
    assert stream["8"] == bad_strings["8"]


def test_complex_dict_grabbing(complex_dict):
    """Test loading a complex dict and grabbing specific keys."""

    assert json.loads(complex_dict)

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    sub_list = dict_1["sub_list"]
    assert next(sub_list) == "a"
    list_2 = stream["list_2"]
    next(list_2)
    dict_2 = next(list_2)
    sub_list = dict_2["sub_list"]
    assert next(sub_list) == "j"


def test_complex_dict_passed_key_raises(complex_dict):
    """
    Test loading a complex dict and attempting to grab a specific key that has been passed raises.
    """

    assert json.loads(complex_dict)

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    assert dict_1["dict_name"] == "one"
    with pytest.raises(KeyError, match="obects_id"):
        stream["obects_id"]


def test_complex_dict_passed_reference_raises(complex_dict):
    """
    Test loading a complex dict and attempting to grab a data from a saved reference that has
    been passed raises.
    """

    assert json.loads(complex_dict)

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    sub_dict = dict_1["sub_dict"]
    sub_list = dict_1["sub_list"]
    list_2 = stream["list_2"]
    next(list_2)
    with pytest.raises(KeyError, match="sub_dict_id"):
        sub_dict["sub_dict_id"]
    with pytest.raises(StopIteration):
        next(sub_list)


# complex_dict is 1518 bytes
@pytest.mark.parametrize(
    ("chunk_size", "expected_chunks"), ((10, 152), (50, 31), (100, 16), (5000, 1))
)
def test_complex_dict_buffer_sizes(chunk_size, complex_dict, expected_chunks):
    """Test loading a complex dict and checking the chunking."""

    assert json.loads(complex_dict)

    bytes_io_chunk = BytesChunkIO(complex_dict.encode(), chunk_size)

    stream = adafruit_json_stream.load(bytes_io_chunk)

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    sub_list = dict_1["sub_list"]
    assert next(sub_list) == "a"
    list_2 = stream["list_2"]
    next(list_2)
    dict_2 = next(list_2)
    sub_list = dict_2["sub_list"]
    assert next(sub_list) == "j"
    for _ in sub_list:
        pass
    with pytest.raises(KeyError):
        stream["list_3"]

    assert bytes_io_chunk.get_chunks_read() == expected_chunks
    assert math.ceil(len(complex_dict) / chunk_size) == expected_chunks


# complex_dict is 1518 bytes
@pytest.mark.parametrize(("chunk_size", "expected_chunks"), ((5, 61), (10, 31), (50, 7), (100, 4)))
def test_complex_dict_not_looking_at_all_data_buffer_sizes(
    chunk_size, complex_dict, expected_chunks
):
    """Test loading a complex dict and checking the chunking."""

    assert json.loads(complex_dict)

    bytes_io_chunk = BytesChunkIO(complex_dict.encode(), chunk_size)

    stream = adafruit_json_stream.load(bytes_io_chunk)

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    sub_list = dict_1["sub_list"]
    assert next(sub_list) == "a"

    assert bytes_io_chunk.get_chunks_read() == expected_chunks
    assert math.ceil(len(complex_dict) / chunk_size) >= (expected_chunks / 4)


def test_incomplete_json_raises():
    """Test incomplete json raises."""

    data = """
    {
        "field_1": 1
    """

    with pytest.raises(json.JSONDecodeError):
        json.loads(data)

    stream = adafruit_json_stream.load(BytesChunkIO(data.encode()))

    with pytest.raises(EOFError):
        stream["field_2"]


def test_as_object(complex_dict):
    """Test loading a complex dict and grabbing parts as objects."""

    assert json.loads(complex_dict)

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    assert dict_1["sub_dict"].as_object() == {
        "sub_dict_id": 1.1,
        "sub_dict_name": "one point one",
    }
    assert dict_1["sub_list"].as_object() == ["a", "b", "c"]
    dict_2 = next(list_1)
    assert dict_2.as_object() == {
        "dict_id": 2,
        "dict_name": "two",
        "sub_dict": {"sub_dict_id": 2.1, "sub_dict_name": "two point one"},
        "sub_list": ["d", "e", "f"],
    }
    assert stream["list_2"].as_object() == [
        {
            "dict_id": 3,
            "dict_name": "three",
            "sub_dict": {"sub_dict_id": 3.1, "sub_dict_name": "three point one"},
            "sub_list": ["g", "h", "i"],
        },
        {
            "dict_id": 4,
            "dict_name": "four",
            "sub_dict": {"sub_dict_id": 4.1, "sub_dict_name": "four point one"},
            "sub_list": ["j", "k", "l"],
        },
    ]


def test_as_object_stream(dict_with_all_types):
    assert json.loads(dict_with_all_types)

    stream = adafruit_json_stream.load(BytesChunkIO(dict_with_all_types.encode()))

    obj = stream.as_object()
    assert obj == {
        "_check": '{"a": 1, "b": [2,3]}',
        "bool": True,
        "dict": {"key": "value"},
        "float": 1.1,
        "int": 1,
        "list": [1, 2, 3],
        "null": None,
        "string": "string",
    }
    assert json.loads(obj["_check"]) == {
        "a": 1,
        "b": [
            2,
            3,
        ],
    }


def test_as_object_that_is_partially_read_raises(complex_dict):
    """Test loading a complex dict and grabbing partially read raises."""

    assert json.loads(complex_dict)

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    assert dict_1["dict_id"] == 1
    with pytest.raises(BufferError):
        dict_1.as_object()


def test_as_object_grabbing_multiple_subscriptable_levels_twice(complex_dict):
    """Test loading a complex dict and grabbing multiple subscriptable levels twice."""

    assert json.loads(complex_dict)

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    assert dict_1["sub_dict"]["sub_dict_id"] == 1.1
    assert dict_1["sub_dict"]["sub_dict_name"] == "one point one"


def test_as_object_grabbing_multiple_subscriptable_levels_again_after_passed_raises(
    complex_dict,
):
    """
    Test loading a complex dict and grabbing multiple subscriptable levels after passing it raises.
    """

    assert json.loads(complex_dict)

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))

    list_1 = stream["list_1"]
    dict_1 = next(list_1)
    assert dict_1["sub_dict"]["sub_dict_id"] == 1.1
    assert next(dict_1["sub_list"]) == "a"
    with pytest.raises(KeyError, match="sub_dict"):
        dict_1["sub_dict"]["sub_dict_name"]


def test_iterating_keys(dict_with_keys):
    """Iterate through keys of a simple object."""

    bytes_io_chunk = BytesChunkIO(dict_with_keys.encode())
    stream = adafruit_json_stream.load(bytes_io_chunk)
    output = list(stream)
    assert output == ["field_1", "field_2", "field_3"]


def test_iterating_keys_get(dict_with_keys):
    """Iterate through keys of a simple object and get values."""

    the_dict = json.loads(dict_with_keys)

    bytes_io_chunk = BytesChunkIO(dict_with_keys.encode())
    stream = adafruit_json_stream.load(bytes_io_chunk)
    for key in stream:
        value = stream[key]
        assert value == the_dict[key]


def test_iterating_items(dict_with_keys):
    """Iterate through items of a simple object."""

    bytes_io_chunk = BytesChunkIO(dict_with_keys.encode())
    stream = adafruit_json_stream.load(bytes_io_chunk)
    output = list(stream.items())
    assert output == [("field_1", 1), ("field_2", 2), ("field_3", 3)]


def test_iterating_keys_after_get(dict_with_keys):
    """Iterate through keys of a simple object after an item has already been read."""

    bytes_io_chunk = BytesChunkIO(dict_with_keys.encode())
    stream = adafruit_json_stream.load(bytes_io_chunk)
    assert stream["field_1"] == 1
    output = list(stream)
    assert output == ["field_2", "field_3"]


def test_iterating_items_after_get(dict_with_keys):
    """Iterate through items of a simple object after an item has already been read."""

    bytes_io_chunk = BytesChunkIO(dict_with_keys.encode())
    stream = adafruit_json_stream.load(bytes_io_chunk)
    assert stream["field_1"] == 1
    output = list(stream.items())
    assert output == [("field_2", 2), ("field_3", 3)]


def test_iterating_complex_dict(complex_dict):
    """Mix iterating over items of objects in objects in arrays."""

    names = ["one", "two", "three", "four"]
    sub_values = [None, "two point one", "three point one", None]

    stream = adafruit_json_stream.load(BytesChunkIO(complex_dict.encode()))

    thing_num = 0
    for index, item in enumerate(stream.items()):
        key, a_list = item
        assert key == f"list_{index+1}"
        for thing in a_list:
            assert thing["dict_name"] == names[thing_num]
            for sub_key in thing["sub_dict"]:
                # break after getting a key with or without the value
                # (testing finish() called from the parent list)
                if sub_key == "sub_dict_name":
                    if thing_num in {1, 2}:
                        value = thing["sub_dict"][sub_key]
                        assert value == sub_values[thing_num]
                    break
            thing_num += 1
