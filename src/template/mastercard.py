import copy
from typing import Dict

from starkbank.iso8583.template.base import Template
from starkbank.iso8583.template.mastercard import mastercard

from ..models.parse import ParseDateDb, ParseHexadecimal, ParseIntegerDb, ParseStringDb
from .base import FieldDb, TemplateDb

custom_mastercard: Dict[str, Template] = copy.deepcopy(mastercard)

for template in custom_mastercard.values():
    template.getField("DE055").parsingRule = ParseHexadecimal()

mastercard_db: TemplateDb = TemplateDb(
    fields=[
        FieldDb(name="MTI", parse=ParseStringDb()),
        FieldDb(name="DE002", parse=ParseStringDb()),
        FieldDb(name="DE003", parse=ParseStringDb()),
        FieldDb(name="DE004", parse=ParseIntegerDb()),
        FieldDb(name="DE012", parse=ParseDateDb()),
        FieldDb(name="DE014", parse=ParseDateDb()),
        FieldDb(name="DE022", parse=ParseStringDb()),
        FieldDb(name="DE023", parse=ParseStringDb()),
        FieldDb(name="DE024", parse=ParseStringDb()),
        FieldDb(name="DE025", parse=ParseStringDb()),
        FieldDb(name="DE026", parse=ParseIntegerDb()),
        FieldDb(name="DE031", parse=ParseStringDb()),
        FieldDb(name="DE033", parse=ParseStringDb()),
        FieldDb(name="DE038", parse=ParseStringDb()),
        FieldDb(name="DE040", parse=ParseStringDb()),
        FieldDb(name="DE041", parse=ParseStringDb()),
        FieldDb(name="DE042", parse=ParseStringDb()),
        FieldDb(name="DE043", parse=ParseStringDb()),
        FieldDb(name="DE049", parse=ParseStringDb()),
        FieldDb(name="DE063", parse=ParseStringDb()),
        FieldDb(name="DE093", parse=ParseStringDb()),
        FieldDb(name="DE094", parse=ParseStringDb()),
        FieldDb(name="PDS0023", parse=ParseStringDb()),
        FieldDb(name="PDS0027", parse=ParseStringDb()),
        FieldDb(name="PDS0052", parse=ParseStringDb()),
        FieldDb(name="PDS0148", parse=ParseStringDb()),
        FieldDb(name="PDS0158", parse=ParseStringDb()),
        FieldDb(name="PDS0165", parse=ParseStringDb()),
        FieldDb(name="PDS0170", parse=ParseStringDb()),
        FieldDb(name="PDS0220", parse=ParseStringDb()),
        FieldDb(name="PDS0375", parse=ParseStringDb()),
    ]
)
