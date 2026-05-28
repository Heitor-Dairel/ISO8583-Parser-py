from typing import Dict, List, Set

from ..models import TypeIpmDb


class FieldDb:
    def __init__(self, name: str, parse: object, custom: bool = False) -> None:
        self.name: str = name
        self.parse: object = parse
        self.custom: bool = custom

        return None

    def parsing(self, data_element: str) -> TypeIpmDb:

        key_custom: Set[str] = {"DE063", "PDS0158"}

        if self.name in key_custom and self.custom:
            return self.parse.field(
                data_element=data_element, name=self.name, custom=self.custom
            )

        return self.parse.field(data_element=data_element, name=self.name)


class TemplateDb:
    _field_by_name: Dict[str, FieldDb] = {}

    def __init__(self, fields: List[FieldDb]) -> None:
        self._field_by_name = {field.name: field for field in fields}

        return None

    def get_field(self, name: str) -> FieldDb:
        return self._field_by_name[name]
