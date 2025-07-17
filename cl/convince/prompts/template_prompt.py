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

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from cl.runtime import RecordMixin
from cl.runtime.log.exceptions.user_error import UserError
from cl.runtime.primitive.case_util import CaseUtil
from cl.runtime.records.for_dataclasses.extensions import required
from cl.runtime.records.protocols import TDataDict
from cl.runtime.records.type_util import TypeUtil
from cl.runtime.schema.type_cache import TypeCache
from cl.runtime.serializers.data_serializers import DataSerializers
from cl.runtime.serializers.key_serializers import KeySerializers
from cl.convince.prompts.prompt import Prompt


@dataclass(slots=True, kw_only=True)
class TemplatePrompt(Prompt, ABC):
    """Uses a template to render the prompt, param names are PascalCase in curly braces."""

    template: str = required()
    """Uses a template to render the prompt, param names are PascalCase in curly braces."""

    params_type: str = required()
    """Record whose pascalized fields are used as template parameters in ClassName format."""

    def render(self, params: RecordMixin) -> str:
        """Use data from the parameters object of 'params_type' to render the template."""
        # Check params type
        self._check_params_type(params)
        # Serialize and convert keys to PascalCase
        params_dict = DataSerializers.DEFAULT.serialize(params)
        params_dict_with_pascal_case_keys = {
            CaseUtil.snake_to_pascal_case(k): v for k, v in params_dict.items() if v is not None
        }
        # Render
        try:
            result = self._render(params_dict_with_pascal_case_keys)
        except KeyError as e:
            field_name = str(e)
            params_key_str = KeySerializers.DELIMITED.serialize(params.get_key())
            present_keys_str = "".join(f"  - {x}\n" for x in params_dict_with_pascal_case_keys.keys())
            raise UserError(
                f"Parameter required by prompt is either None or not a field of the parameters object.\n"
                f"Prompt key='{self.prompt_id}'\n"
                f"Parameter name: {field_name}\n"
                f"Parameters object type={TypeUtil.name(params)} and key='{params_key_str}'\n"
                f"Available non-empty fields of the parameters object:\n{present_keys_str}\n"
            )
        return result

    @abstractmethod
    def _render(self, dict_with_pascal_case_keys: TDataDict) -> str:
        """Protected method performing the actual rendering, must throw KeyError if a parameter is missing."""

    def _check_params_type(self, params: Any) -> None:
        """Check that params object is an instance of the right type."""
        if params is None:
            raise UserError(f"Params field is empty for prompt '{self.prompt_id}'.")
        params_type = TypeCache.get_class_from_type_name(self.params_type)
        if not isinstance(params, params_type):
            raise UserError(
                f"Parameters object for prompt {self.prompt_id} has type {TypeUtil.name(params)} which "
                f"is not a subclass of the expected type {self.params_type}."
            )
