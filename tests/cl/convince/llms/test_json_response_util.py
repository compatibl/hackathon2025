# Copyright (C) 2023-present The Project Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest
from cl.convince.llms.json_response_util import JsonResponseUtil


def test_fix_json_format() -> None:
    test_cases = [
        # Test basic valid JSON
        ('{"key": "value"}', '{"key": "value"}'),
        # Test single quotes to double quotes
        ("{'key': 'value'}", '{"key": "value"}'),
        # Test possessive form
        ("{'key': \"It's a test\"}", '{"key": "It\'s a test"}'),
        # Test possessive form with escaped single quotes
        ("{'key': 'It\\'s a test'}", '{"key": "It\'s a test"}'),
        # Test boolean values
        ("{'key': True, 'key2': False}", '{"key": true, "key2": false}'),
        # Test None values
        ("{'key': None}", '{"key": "None"}'),
        # Test mixed quotes
        ("{'key': \"He said, 'hello'\"}", '{"key": "He said, "hello""}'),
        # Test trailing comma fix
        ("{'key': 'value',}", '{"key": "value" }'),
        # Test more complex JSON
        (
            "{'key': 'value', 'key2': 'value2', 'key3': True, 'key4': None}",
            '{"key": "value", "key2": "value2", "key3": true, "key4": "None"}',
        ),
        # Test handling of nested JSON
        ("{'outer': {'inner': 'value'}}", '{"outer": {"inner": "value"}}'),
        # Test invalid JSON fix attempt
        (
            "{'key': 'value', 'key2': 'value2', 'key3': True, 'key4': None,}",
            '{"key": "value", "key2": "value2", "key3": true, "key4": "None" }',
        ),
        # Test JSON with nested quotes
        ("{'key': 'value with \"double quotes\" inside'}", '{"key": "value with "double quotes" inside"}'),
        # Test JSON with escaped quotes
        (
            "{'key': 'value with \\\"escaped double quotes\\\" inside'}",
            '{"key": "value with \'escaped double quotes\' inside"}',
        ),
        # Test single quotes around keys
        ("{'key1': 'value1', 'key2': 'value2'}", '{"key1": "value1", "key2": "value2"}'),
        # Test underscore escape in a key
        ('{"key\_1": "value"}', '{"key_1": "value"}'),
        ('{"key\\_1": "value"}', '{"key_1": "value"}'),
        # Test underscore escape in a value
        ('{"key_1": "value\_1"}', '{"key_1": "value_1"}'),
        ('{"key_1": "value\\_1"}', '{"key_1": "value_1"}'),
        # Test underscore escape with quotes in a value
        ('{"key_1": "value\'_1"}', '{"key_1": "value\'_1"}'),
        # Special characters mixed with quotes
        ("{'key': 'Special!@#$%^&*()_+=-{}[]:\";<>?,./\\'key'}", '{"key": "Special!@#$%^&*()_+=-{}[]:";<>?,./\'key"}'),
        # Valid empty json string
        (" {}  ", " {}  "),
        (" {  \n }  ", " {  \n }  "),
        ("[ {} ]", "[ {} ]"),
    ]

    for input_str, expected_output in test_cases:
        assert JsonResponseUtil.fix_json_format(input_str) == expected_output


def test_extract_json_content() -> None:
    test_cases = [
        ("```json[]```", "[]"),  # A valid empty list in json
        ("```json[{}, {}]```", "[{}, {}]"),
        ('```json[{"key1": "value1"}, "key2": "value2"}]```', '[{"key1": "value1"}, "key2": "value2"}]'),
        ("```json{}```", "{}"),
        ("```json{'key': \"He said, 'hello'\"}", "{'key': \"He said, 'hello'\"}"),
        (
            '```json[ {"Key_1": "Value_1" }, { "Key_2": "Value_2", "Key_3": [1, 3, 4]} ]```',
            '[ {"Key_1": "Value_1" }, { "Key_2": "Value_2", "Key_3": [1, 3, 4]} ]',
        ),
    ]

    for json_string, expected_output in test_cases:
        assert JsonResponseUtil.extract_json_content(json_string) == expected_output


@pytest.mark.skip(reason="Review diffs after conversion to code from pytest parameterize")
def test_normalize_unescaped_quotes_and_load_json_str() -> None:
    test_cases = [
        ("{'key': \"He said, 'hello'\"}", '{"key": "He said, \\"hello\\""}'),
        # Test JSON with nested quotes
        ("{'key': 'value with \"double quotes\" inside'}", '{"key": "value with "double quotes" inside"}'),
        # Test JSON with escaped quotes
        (
            "{'key': 'value with \\\"escaped double quotes\\\" inside'}",
            '{"key": "value with \\"escaped double quotes\\" inside"}',
        ),
        # Special characters mixed with quotes
        (
            "{'key': 'Special!@#$%^&*()_+=-{}[]:\";<>?,./\\'key'}",
            '{"key": "Special!@#$%^&*()_+=-{}[]:\\";<>?,./\\"key"}',
        ),
    ]

    for input_str, expected_output in test_cases:
        fixed_str = JsonResponseUtil.fix_json_format(input_str)
        assert JsonResponseUtil.normalize_unescaped_quotes_and_load_json_str(fixed_str) == expected_output


def test_fix_json_format_exceptions() -> None:
    test_cases = [
        # Test invalid JSON (with strict mode should raise ValueError)
        ("{'key': 'value', 'key2': 'value2', 'key3': True, 'key4': None,", ValueError),
        # Incorrect handling of True, False, None
        ("{'key': Truely, 'key2': False, 'key3': Noneable}", ValueError),
        # Handling of commas in JSON arrays
        ("{'key': ['value1', 'value2',]}", ValueError),
    ]

    for input_str, expected_exception in test_cases:
        with pytest.raises(expected_exception):
            fixed_str = JsonResponseUtil.fix_json_format(input_str)
            JsonResponseUtil.normalize_unescaped_quotes_and_load_json_str(fixed_str, strict=True)


def test_normalize_unescaped_quotes_and_load_json_str_cases() -> None:
    test_cases = [
        (
            '{"key": "value with an " quote "", "key_2": "value_2 ; " quote "}',
            '{"key": "value with an \\" quote \\"", "key_2": "value_2 ; \\" quote "}',
        ),
        (
            '{"key": "value with an "quote" and another " quote"}',
            '{"key": "value with an \\"quote\\" and another \\" quote"}',
        ),
        (
            '{"key": "value with already escaped \\" quote", "key_2": "value_2\\""}',
            '{"key": "value with already escaped \\" quote", "key_2": "value_2\\""}',
        ),
        ('{"key": "value without quotes"}', '{"key": "value without quotes"}'),
        ('{"key": "value without quotes", "key_2": "value_2"}', '{"key": "value without quotes", "key_2": "value_2"}'),
        (
            "{ "
            '   "key1": [ "1", "1.5 - T"], '
            '   "key2":"The text, another text. It outlines "Something1", "Something1", and other things '
            "}.",
            "{}",
        ),
    ]

    for input_str, expected_output in test_cases:
        assert JsonResponseUtil.normalize_unescaped_quotes_and_load_json_str(input_str) == expected_output


def test_normalize_unescaped_quotes_endless_loop() -> None:
    test_cases = [
        '{"key": "val"ue}"',
        "{ "
        '   "key1": [ "1", "1.5 - T"], '
        '   "key2":"The text, another text. It outlines "Something1", "Something1", and other things '
        "}.",
    ]

    for input_str in test_cases:
        with pytest.raises(ValueError):
            JsonResponseUtil.normalize_unescaped_quotes_and_load_json_str(input_str, strict=True)


if __name__ == "__main__":
    pytest.main([__file__])
