from dataclasses import dataclass

import numpy as np
import pandas as pd


def read_csv_file_with_header(filename) -> pd.DataFrame:
    """Read CSV file with pandas and header row
    Args:
        filename (.csv): CSV file with columns: id, short, long, description

    Returns:
        pd.DataFrame: [description]
    """
    df = pd.read_csv(filename, encoding="utf-8", header=0)
    return df


def escape_latex_special_chars(df: pd.DataFrame) -> pd.DataFrame:
    """Escape special LaTeX characters in dataframe

        This function replaces special characters in the dataframe with
        escaped versions.  Currently, the following characters are replaced:
        \, &, #, %, {, }, _, ~

    Args:
        df (pd.DataFrame): [description]

    Returns:
        pd.DataFrame: [description]
    """
    df = df.replace(r"\\", r"\\textbackslash", regex=True)
    df = df.replace("&", r"\&", regex=True)
    df = df.replace("#", r"\#", regex=True)
    df = df.replace("%", r"\%", regex=True)
    df = df.replace("{", r"\{", regex=True)
    df = df.replace("}", r"\}", regex=True)
    df = df.replace("_", r"\_", regex=True)
    df = df.replace("~", r"\\textasciitilde", regex=True)

    return df


@dataclass
class AcroData:
    """Acronym data class

    Attributes:
        id (str): acronym id
        short (str): acronym short form
        long (str): acronym long form
        description (str): acronym description
    """

    id: str
    short: str
    long: str
    description: str
    tag: str = ""

    def __str__(self):
        return f"{self.id} {self.short} {self.long} {self.description} {self.tag}"


# Convert AcroData to acro formatted text
@dataclass
class AcroConverter(AcroData):
    """
    Convert AcroData into LaTeX formatted DelclareAcronym structure.
    See format below:

        \DeclareAcronym{<id>}{
            short = <short> or {-},
            long = <long>,
            extra = {%
            <description>
            },
            first-style=<long>, # only for short=None
            sort={<long>}, # only for short=None
        }
    """

    def convert_short(self):
        """_summary_"""
        # check if short is nan
        if pd.isnull(self.short):
            short = "{-}"
        else:
            short = self.short
        return f"   short = {short},\n"

    def convert_long(self):
        """_summary_"""
        return f"   long = {{{self.long}}},\n"

    def convert_description(self):
        """_summary_"""
        if pd.isnull(self.description):
            description_str = "   extra = ,\n"
        else:
            description_str = f"   extra = {{%\n       {self.description}\n   }},\n"
        return description_str

    def convert_tag(self):
        """_summary_"""
        # check if tag is nan
        if pd.isnull(self.tag):
            tag_str = "{-}"
        else:
            tag_str = f"{{{self.tag}}}"
        return f"   tag = {tag_str},\n"

    def convert_to_acro(self):
        """_summary_"""
        # convert_id
        id_str = f"\DeclareAcronym{{{self.id}}}{{\n"
        # convert short
        short_str = self.convert_short()
        # convert long
        long_str = self.convert_long()
        # convert description
        description_str = self.convert_description()
        # convert tag
        tag_str = self.convert_tag()

        # Combine required strings
        full_str = "".join(
            [
                id_str,
                short_str,
                long_str,
                description_str,
                tag_str,
            ]
        )

        # if isnull(short), add first_style and sort fields
        if pd.isnull(self.short):
            full_str += f"   first-style = long,\n"
            full_str += f"   sort = {self.long},\n"

        # Close bracket
        full_str += "}\n"
        return full_str


def write_acro_list_to_file(acro_list, output_file):
    """_summary_"""
    with open(output_file, "w") as f:
        for acro in acro_list:
            f.write(acro.convert_to_acro())
            f.write("\n")

    print(20 * "*")
    print(f"{len(acro_list)} acronyms written to {output_file}")
    print(20 * "*")


def test():
    """_summary_"""
    acro = AcroConverter("id", "short", "long", "description")
    print(acro.convert_to_acro())

    a_convert = AcroConverter("A", "A", "long text", "A nice long description")
    print(a_convert.convert_to_acro())

    b_convert = AcroConverter("B", np.nan, "long text", "A nice long description")
    print(b_convert.convert_to_acro())

    c_convert = AcroConverter("C", "C", "long text", np.nan)
    print(c_convert.convert_to_acro())

    d_convert = AcroConverter("D", "D", "long text", "Multi-line\n\n text")
    print(d_convert.convert_to_acro())

    long_str = "Some special chars: & # % { } _ ~"
    e_convert = AcroConverter("E", "E", "long text", long_str)
    print(e_convert.convert_to_acro())

    a = AcroConverter(
        id="A", short="A", long="long text", description="A nice long description"
    )
    print(a.convert_to_acro())

    adict = dict(
        id="ADict",
        short="ADict",
        long="long text",
        description="A nice long description",
    )
    aA = AcroConverter(**adict)
    print(aA.convert_to_acro())


def display_formatted_acro_list(acro_list):
    """Print formatted LaTeX acro list to the screen"""
    for acro in acro_list:
        print(acro.convert_to_acro())


def main():
    """_summary_"""
    input_file = "acroList.csv"
    # read data file with header
    df = read_csv_file_with_header(input_file)
    # df = escape_latex_special_chars(df)

    # Convert pandas dataframe to list of AcroConverter objects
    acro_list = [AcroConverter(**row) for row in df.to_dict("records")]
    # acro_list = []
    # for row in df.to_dict("records"):
    #     acro_list.extend(AcroConverter(**row))

    # Display list of converted AcroData objects
    display_formatted_acro_list(acro_list)

    # write list of AcroData objects to .tex file
    output_file = input_file.split(".")[0] + ".tex"
    write_acro_list_to_file(acro_list, output_file)

    return acro_list


if __name__ == "__main__":
    test()

    acro_list = main()
