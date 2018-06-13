"""
This module is used for the identification of the data.
ID is mainly from the external definition of each file/webpage.
Address is the corresponding address data to the specified ID file/webpage.

Functions:
    ID() -> {'  ID': id}
    address(pq_doc) ->  {' Address': add, ' City': city, ' State': state,
                         ' Zip': zip code}
"""


import re
import sys
from pyquery import PyQuery as pq

def ID(id):
    return {"   ID": id}

def address(pq_doc):
    """address(pq_doc) -> dict

    :param pq_doc: PyQuery object of source code.
    :return: Dict as {' Address': add, ' City': city, ' State': state,
                       ' Zip': zip code}
    """
    css_selector_main = '[style="float:left"]'
    address_all = pq_doc(css_selector_main).text()
    # The address would contain dash symbol '-' between the street number, or
    # the middle of the total address (useless and would be deleted), or not.
    # The following regex is used to get the most useful part of the address.
    add = re.match(r'[0-9]+(-[0-9]+)?.*?(?=($|-))', address_all).group()

    # The following part contains the city, state and zip of the address.
    css_selector_detail = '.subHeaderContainer b'
    # The detail address may have 1 or more lines with(out) the main address.
    address_detail = ", ".join(
        item.text() for item in pq_doc(css_selector_detail).items()
    )

    city = re.search(r'(?<=(,\s))?[A-Z][A-Za-z\s]*(?=(,\s[A-Z]{2}\s[0-9]{5}))',
                     address_detail).group()
    state = re.search(r'(?<=(,\s))[A-Z]{2}(?=(\s[0-9]{5}))', address_detail)\
        .group()
    zip_code = re.search(r'(?<=[A-Z]{2}\s)[0-9]{5}', address_detail).group()
    add_result = dict(zip(["  Address", "  City", "  State", "  Zip"],
                      [add, city, state, zip_code]))
    return add_result

