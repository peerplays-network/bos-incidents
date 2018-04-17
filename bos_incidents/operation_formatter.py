import datetime
import json

from .. import addresses
import os
import io
import jsonschema
import uuid

import hashlib


def decode_operation(operation):
    """ The given operation comes directly from the blockchain and is here reformatted.
        This is done to better suit the needs of our processing and also due to the fact
        that the resulting operations dict can't have nested dicts.

        :param operation: operation as given by blockchain monitor
        :type operation: dict
    """
    memo = operation["op"][1].get("memo", "unknown")

    new_operation = {
        "block_num": operation.get("block_num"),
        "memo": json.dumps(memo),
        "from": operation["op"][1]["from"],
        "to": operation["op"][1]["to"],
        "amount_value": operation["op"][1]["amount"]["amount"],
        "amount_asset_id": operation["op"][1]["amount"]["asset_id"],
        "expiration": datetime.datetime.strptime(
            operation["expiration"], "%Y-%m-%dT%H:%M:%S").timestamp(),
        "fee_value": operation["op"][1]["fee"]["amount"],
        "fee_asset_id": operation["op"][1]["fee"]["asset_id"]
    }

    try:
        memo = addresses.split_memo(operation["decoded_memo"])
    except KeyError:
        memo = addresses.split_memo("unknown")
    except ValueError:
        memo = addresses.split_memo("unknown")

    if operation.get("message"):
        new_operation["message"] = operation["message"]

    chain_identifier = str(
        operation.get("transaction_id")
    ) + ":" + str(
        operation.get("op_in_tx")
    )

    if not memo["incident_id"]:
        memo["incident_id"] = chain_identifier

    data = {
        "chain_identifier": chain_identifier,
        "customer_id": memo["customer_id"],
        "incident_id": memo["incident_id"]
    }

    new_operation.update(data)

    return new_operation


OPERATION_SCHEMA = None


def validate_operation(operation):
    """
        Validates the given reformatted operation against the json schema given by
        :file:`operation_schema.json`

        :param operation: operation formatted as returned by :func:`decode_operation`
        :type operation:
    """
    global OPERATION_SCHEMA
    if not OPERATION_SCHEMA:
        schema_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "operation_schema.json"
        )
        OPERATION_SCHEMA = json.loads(io.open(schema_file).read())
    # to validate date format against zulu time, rfc import is needed
    jsonschema.validate(operation,
                        OPERATION_SCHEMA,
                        format_checker=jsonschema.FormatChecker())
