import os
from ttp import ttp

class TTPParserHelper:
    def __init__(self, ttp_template_file):
        """
        Initialize the TTP parser helper with the template file path.

        :param ttp_template_file: Path to the TTP template file.
        """
        self.ttp_template_file = ttp_template_file

    def parse(self, input_data):
        """
        Parses the provided input data using the TTP template file.

        :param input_data: The raw SSH output to be parsed.
        :return: Always returns a list of parsed results, even if only one instance is found.
        """
        if not os.path.exists(self.ttp_template_file):
            raise FileNotFoundError(f"TTP template file {self.ttp_template_file} not found.")

        # Load the template from the file
        with open(self.ttp_template_file, 'r') as template_file:
            template_content = template_file.read()

        # Initialize the TTP parser
        parser = ttp(data=input_data, template=template_content)

        # Parse the data
        parser.parse()

        # Get the parsed result
        result = parser.result()

        # Normalize the result to always be a list
        if isinstance(result, list) and len(result) > 0:
            result = result[0]  # First result set (default in TTP)

        # Check if the result is a dictionary and convert it to a list of dictionaries if needed
        if isinstance(result, dict):
            return [result]  # Wrap the single dictionary in a list
        return result
