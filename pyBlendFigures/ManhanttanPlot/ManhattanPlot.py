from pyBlendFigures import BlendController

from miscSupports import validate_path, open_setter, decode_line, terminal_time, normalisation_min_max


class ManhattanPlot(BlendController):
    def __init__(self, blender_path, working_directory, gwas_output_path, chromosome_header="CHR", snp_header="SNP",
                 base_position_header="BP", p_value_header="P"):
        super().__init__(blender_path, working_directory)

        # Validate the path is valid to the summary file and determine its zipped status
        self._summary_file = validate_path(gwas_output_path)
        self._zipped = self._summary_file.suffix == ".gz"

        # Isolate the header indexes from the headers, validating we have a matching header name for each of our
        #   attributes
        self.chr_h, self.snp_h, self.bp_h, self.p_h = self._set_summary_headers(
            chromosome_header, snp_header, base_position_header, p_value_header)
        self.header_indexes = [self.chr_h, self.snp_h, self.bp_h, self.p_h]

        print(self.header_indexes)


    # def _create_temp_file(self):
    #
    #     print(f"Start {terminal_time()}")
    #     with open_setter(self._summary_file)(self._summary_file) as file:
    #         # Skip the header
    #         file.readline()
    #
    #         for index, line_byte in enumerate(file):
    #             if index % 10000 == 0:
    #                 print(index)
    #
    #             line = [v for i, v in enumerate(decode_line(line_byte, self._zipped)) if i in self.header_indexes]
    #
    #     print(f"End {terminal_time()}")

    def _set_summary_headers(self, chromosome_header, snp_header, base_position_header, p_value_header):
        """
        Validate which columns are the chromosome, snp, base position and p value.

        To do this, each name provided or the respective default is checked against the first row of the summary file.
        If all are present, the indexes are returned in the order of the header input arguments so they can be assigned
        and used to isolate values later.

        :param chromosome_header: chromosome header name
        :type chromosome_header: str

        :param snp_header: snp header name
        :type snp_header: str

        :param base_position_header: base position header name
        :type base_position_header: str

        :param p_value_header: p value header
        :type p_value_header: str

        :return: A list of [chromosome_header_index, snp_header_index, base_position_index, p_value_index]
        :rtype: list[int, int, int, int]

        :raises KeyError: If a header provided was not found in the decoded headers
        """

        # Decode the headers
        with open_setter(self._summary_file)(self._summary_file) as file:
            decoded_headers = decode_line(file.readline(), self._zipped)
        file.close()

        header_indexes = []
        for header in [chromosome_header, snp_header, base_position_header, p_value_header]:
            if header in decoded_headers:
                header_indexes.append(decoded_headers.index(header))
            else:
                raise KeyError(f"{header} was not found in {decoded_headers}")
        return header_indexes


if __name__ == '__main__':
    bp = r"C:\Users\Samuel\Documents\Blender\blender-2.83.2-windows64\blender.exe"
    working_dir = r"C:\Users\Samuel\PycharmProjects\pyBlendFigures\Tests\ManhattanTests"
    output_path = r"Z:\UKB\GeographicID\Paper Data Extraction\SB_Papers\GWAS\Results\SF_1_imputed.txt.gz"
    mm = ManhattanPlot(bp, working_dir, output_path, p_value_header="P_BOLT_LMM_INF")