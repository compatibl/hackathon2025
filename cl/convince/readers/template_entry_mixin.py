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

import difflib
from abc import ABC
from abc import abstractmethod
from typing import Generic
from cl.runtime.contexts.db_context import DbContext
from cl.runtime.records.key_mixin import KeyMixin
from cl.runtime.records.protocols import TKey
from cl.runtime.serializers.bootstrap_serializers import BootstrapSerializers
from cl.runtime.serializers.yaml_encoders import YamlEncoders
from cl.convince.readers.entry_mixin import EntryMixin


class TemplateEntryMixin(Generic[TKey], EntryMixin[TKey], ABC):
    """
    Optional generic mixin for a text entry with a describe_correction method that uses a template.
    Declare MyEntryTemplate as MyEntryTemplate(MyKey, TemplateEntryMixin[MyKey]).
    """

    __slots__ = ()
    """To prevent creation of __dict__ in derived types."""

    @property
    @abstractmethod
    def template(self) -> KeyMixin:
        """Template used to validate the entry."""

    def describe_correction(self) -> str | None:
        # Load the template from DB
        template_type = type(self.template)
        template = DbContext.load_one(template_type, self.template)
        # Render
        rendered_template = template.render(self)  # noqa
        if self.text == rendered_template:
            return None
        else:
            # Create unified diff
            input_lines = self.text.splitlines(keepends=True)
            rendered_lines = rendered_template.splitlines(keepends=True)
            diff_lines = difflib.ndiff(
                input_lines,
                rendered_lines,
                linejunk=lambda x: False,
                charjunk=lambda x: False,
            )
            filtered_diff_lines = [line for line in diff_lines if not line.startswith("?")]
            diff_str = "\n".join(filtered_diff_lines)

            # Remove fields includes elsewhere
            params_dict = BootstrapSerializers.FOR_UI.serialize(self)
            del params_dict["Text"]
            del params_dict["Template"]
            params_yaml = YamlEncoders.DEFAULT.encode(params_dict)

            # Return correction string
            template_body = self.template.body  # noqa
            return (
                f"The template and data from your previous response did not match the input text.\n"
                f"Please provide a new response that corrects the differences described below.\n\n"
                f"Template body:\n\n{template_body}\n\nTemplate parameters:\n\n{params_yaml}\n\n"
                f"Unified diff (---InputText +++RenderedText):\n\n{diff_str}\n\n"
            )
