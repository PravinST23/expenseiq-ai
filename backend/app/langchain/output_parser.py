"""
LangChain Output Parser

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import json


class OutputParser:
    """
    Parse AI output.
    """

    @staticmethod
    def parse(
        response: dict,
    ) -> dict:

        if isinstance(
            response,
            dict,
        ):
            return response

        if isinstance(
            response,
            str,
        ):
            return json.loads(response)

        raise ValueError(
            "Unsupported response type."
        )


output_parser = OutputParser()