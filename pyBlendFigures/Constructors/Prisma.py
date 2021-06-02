from miscSupports import write_yaml
from pathlib import Path
import textwrap


class Prisma:
    def __init__(self, line_width=70):
        self.plot_dict = {}

        self.line_width = line_width

    def add_element(self, box_text, column, row):
        """
        Add an element to the Prisma Plot

        :param box_text: The text you want to add
        :type box_text: str

        :param column: The column index position you want to use
        :type column: int

        :param row: The row index position you want to use
        :type row: int

        :return: Nothing, append element to plot_dict then stop
        :rtype: None
        """

        # Split the text on line width, then add in custom breaks
        text_list = textwrap.wrap(box_text, self.line_width, replace_whitespace=False)

        # Create new lines at the end of each element in the list then add this to the plot dict
        out_text = "".join([f"{text}\n" if i != len(text_list) - 1 else text for i, text in enumerate(text_list)])
        self.plot_dict[f"{column}-{row}"] = {"Text": out_text, "Col": column, "Row": row}

    def prisma_links(self):
        """
        Links for prisma, by default sets all columns bar the first to be False and all rows to be True

        :return: A dict of Columns: {Col_number: True/False, Row_Number: True/False}
        :rtype: dict
        """

        # Extract the column and row ids
        key_ids = list(key.split("-") for key in self.plot_dict.keys())
        columns = sorted(list(set([col for col, row in key_ids])))
        rows = sorted(list(set([row for col, row in key_ids])))

        # Set all columns to be false and all rows to be true apart from the first column, which we override to be True
        link_dict = {"Columns": {col: False for col in columns}, "Rows": {row: True for row in rows}}
        link_dict["Columns"][min(columns)] = True
        return link_dict

    def write_prisma_config(self, links, write_directory, write_name):
        """
        Write the Prisma config for BlendFigure to use

        :param links: Links dict
        :type links: dict

        :param write_directory: Directory to save the file to
        :type write_directory: str | Path

        :param write_name: The name of the file
        :type write_name: str

        :return: Nothing, write file then stop
        :rtype: None
        """
        write_yaml({"Links": links, "Positions": self.plot_dict}, write_directory, write_name)
