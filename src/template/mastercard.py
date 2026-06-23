import copy
from typing import Dict

from starkbank.iso8583.template.base import Template
from starkbank.iso8583.template.mastercard import mastercard

from ..models.parse import ParseHexadecimal

custom_mastercard: Dict[str, Template] = copy.deepcopy(mastercard)

for template in custom_mastercard.values():
    template.getField("DE055").parsingRule = ParseHexadecimal()
