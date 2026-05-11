from datetime import datetime
from typing import Any, Dict, Final, List, Optional, Union

from ..models import TypeIpm, TypeIpmDb


class ParseInteger:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str) -> Union[int, float]:
        if name == "DE004":
            return int(data_element) / 100

        return int(data_element)


class ParseStringDb:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str, custom: bool = False) -> str:
        if custom and name == "DE063":
            return data_element[:3]

        if custom and name == "PDS0158":
            return data_element[:2]

        return data_element


class ParseDate:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str) -> str:

        if name == "DE012":
            return datetime.strptime(data_element, "%y%m%d%H%M%S").strftime(
                "%d/%m/%Y %H:%M:%S"
            )

        return datetime.strptime(data_element, "%y%m").strftime("%y/%m")


class ParseField:
    def __init__(self, name: str, parse: object, custom: bool = False) -> None:
        self.name: str = name
        self.parse = parse
        self.custom: bool = custom

    def parsing(self, data_element: str) -> TypeIpmDb:

        if self.name in {"DE063", "PDS0158"} and self.custom:
            return self.parse.field(
                data_element=data_element, name=self.name, custom=self.custom
            )

        return self.parse.field(data_element=data_element, name=self.name)


class TemplateDb:
    _field_by_name: Dict[str, ParseField] = {}

    def __init__(self, fields: List[ParseField]) -> None:
        self._field_by_name = {field.name: field for field in fields}

    def get_field(self, name: str) -> ParseField:
        return self._field_by_name[name]


class BeautifyIpmDb:
    _DATA_ELEMENTS_MESSAGE: Final[List[List[str]]] = [
        ["MTI", "DE"],
        ["DE002", "DE"],
        ["DE003", "DE"],
        ["DE004", "DE"],
        ["DE012", "DE"],
        ["DE014", "DE"],
        ["DE022", "DE"],
        ["DE023", "DE"],
        ["DE024", "DE"],
        ["DE025", "DE"],
        ["DE026", "DE"],
        ["DE031", "DE"],
        ["DE033", "DE"],
        ["DE038", "DE"],
        ["DE040", "DE"],
        ["DE041", "DE"],
        ["DE042", "DE"],
        ["DE043", "DE"],
        ["DE049", "DE"],
        ["DE063", "DE"],
        ["DE093", "DE"],
        ["DE094", "DE"],
        ["PDS0023", "PDS"],
        ["PDS0052", "PDS"],
        ["PDS0148", "PDS"],
        ["PDS0158", "PDS"],
        ["PDS0165", "PDS"],
        ["PDS0170", "PDS"],
        ["PDS0220", "PDS"],
        ["PDS0375", "PDS"],
        ["DE063", "DE"],
        ["PDS0158", "PDS"],
    ]

    def __init__(self, template: TemplateDb, elements: TypeIpm) -> None:
        self.elements: TypeIpm = elements
        self.template = template

    def parse(
        self,
    ) -> List[List[TypeIpmDb]]:

        parse_db: List[List[TypeIpmDb]] = []
        parse_db_append = parse_db.append

        for message in self.elements:
            if message["MTI"] == "1240":
                parse_db_append(self._loop_element(message=message))

        return parse_db

    def _loop_element(
        self,
        message: Dict[str, Any],
    ) -> List[TypeIpmDb]:

        parse_elements: List[TypeIpmDb] = []
        parse_elements_append = parse_elements.append

        for element in self._DATA_ELEMENTS_MESSAGE:
            key: str = element[1]
            value: str = element[0]
            data_element: TypeIpmDb = self._get_element(
                message=message, name=value, type_element=key
            )

            parse_elements_append(data_element)

        return parse_elements

    def _get_element(
        self,
        message: Dict[str, Any],
        name: str,
        type_element: str,
    ) -> TypeIpmDb:

        data_element: Optional[str] = None

        if type_element == "DE":
            data_element = message.get(name)

        if type_element == "PDS":
            data_element = message[type_element].get(name)

        if data_element:
            element_ipm: ParseField = self.template.get_field(name=name)
            return element_ipm.parsing(data_element=data_element.strip())

        return data_element
