import os
import io
import json
import jsonschema

from jsonschema.exceptions import ValidationError
from bos_incidents.exceptions import InvalidIncidentFormatException


class IncidentValidator():
    INCIDENT_SCHEMA = None

    def validate_incident(self, incident):
        """
            Validates the given reformatted operation against the json schema given by
            :file:`operation_schema.json`

            :param operation: operation formatted as returned by :func:`decode_operation`
            :type operation:
        """
        if not IncidentValidator.INCIDENT_SCHEMA:
            schema_file = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "incident-schema.json"
            )
            IncidentValidator.INCIDENT_SCHEMA = json.loads(io.open(schema_file).read())
        try:
            # to validate date format against zulu time, rfc import is needed
            jsonschema.validate(incident,
                                IncidentValidator.INCIDENT_SCHEMA,
                                format_checker=jsonschema.FormatChecker())
        except ValidationError:
            raise InvalidIncidentFormatException()
