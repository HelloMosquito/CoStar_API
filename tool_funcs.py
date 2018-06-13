import numpy
import sys


def pairs_gene(pq_doc, css_selector, seg_prefixes,
               add_name=list(), add_value=list(), inp=0):
    """_label_pairs(self, css_selector, seg_prefixes) -> <zip object>

    :param
    :pq_doc: The PyQuery object of web-page source code.
    :css_selector: For specific css selector.
    :seg_prefixes: For add the specific segment title in front of each keys,
        like "Sale" to "Sale_Sole Price, "Building" to "Building_Year Built",...
    :add_name: If there are some additional pairs name, put in as a list,
        default as blank list []
    :add_value: Corresponding to add_name list as the value list,
        default as blank list []
    :inp: As the abbreviation of 'input the choice', it's used for those
        which have two or more same key in the pair-name list. If it's assigned
        in the code, that usually means the choice has been chosen. If it's not
        assigned, there would be "two possible case":
            1. there is no repeated key in the pair-name list, then the
            code will continue normally;
            2. the repeated key hasn't been recognized, it needs to be chosen
            manually.

    :return: A <zip object> of the pair_name list and pair_value list
    """
    assert isinstance(add_name, list) and isinstance(add_value, list), \
        "In tool_funcs.py, label_pairs()," \
        "add_name or add_value is not type of list"

    # filter_doc is the PyQuery doc corresponding to the crawling part
    filter_doc = pq_doc(css_selector).find('.label-value-pair')
    k = [seg_prefixes + '_' + item('span').eq(0).text()
         for item in filter_doc.items()] + add_name
    v = [item('span:gt(0)').text()
         for item in filter_doc.items()] + add_value

    # judge whether there are repeated keys in k-list(pair_name list)
    # and decide which one will be used
    if len(set(k)) != len(k):
        # rep_k is a list contains all repeated keys as
        # (key start position, key, repeat No. of the key)
        rep_k = [(k.index(rep_k), rep_k, k.count(rep_k))
                 for rep_k in set(k)
                 if k.count(rep_k) > 1]
        # for each repeated key, choose one of them
        # del_po is the list containing all the positions of repeated k-v
        # pairs which will be deleted
        del_po = []
        for item in rep_k:
            del_po += select_duplicate_k_v(item, k, v, inp)
        delete_duplicate(del_po, k, v)
    assert len(k) == len(v), \
        "In tool_funcs.py, label_pairs(), pair-length doesn't match" \
        "len(pair_name) != len(pair_value)"
    return zip(k, v)


def delete_duplicate(del_po, k_li, v_li):
    for item in del_po:
        del k_li[item]
        del v_li[item]


def select_duplicate_k_v(item, k_li, v_li, inp):
    """select_duplicate_k_v(item, k_li, v_li, inp) -> del_position list

    This method is used for determining whether there are repeated pair-name
    in the pair-name list, e.g., ["sale", "building", "properties", "sale],
    whose "sale" is the repeated pair-name in this list. If it is, this
    method will return a list to indicate which position of the pair-name
    and pair-value will be delete.

    This method only affect one duplicate item in the list, if there are more
    than one key value duplicated , rerun the method, or build a loop.

    :param:
    :inp: See function 'label_pairs()', by default value of 0 in
        order to be checked in the if statement of '1<=inp<=n'. Otherwise, it
        would go through the check directly.
    :item: A tuple contains 3 parts as (po, k, n) as following
        (repeated key's start position, the repeated key, the No. of the key)
    :k_li: The original pair-name list.
    :v_li: The original pair-value list.
    :k_li_rep_k_idx: The repeated key index in the original pair-name list.
    :rep_k_v: The list contains all values of the repeated key.
    :rep_k_v_set: Convert the rep_k_v list to set (without repeated item).
    :ori_k_idx_inp: A dict contains the original key index(key) and
        repeated ky index(value) plus 1 (+1) as the 'inp' value.
        For example,
        pair-name list is: ['a', 'c' 'bb', 'd', 'bb', 'bb', 'k', 'y', 'bb']
        repeated key list is: ['bb', 'bb', 'bb', 'bb']
        (po, k, n) is: (2, 'bb', 4)
        Thus, the ori_k_idx_inp is {2:1, 4:2, 5:3, 8:4}
        Key of the dict 'ori_k_idx_inp' is the index of the pair-name list.
        Value of the dict 'ori_k_idx_inp' is the repeated time as the 'inp'
        value.
    :inp_ori_k_idx: Switch the key, value of the ori_k_idx_inp as the
        'value':'key' dict.

    :return: A list contains the repeated keys' positions to be deleted.
    """
    po, k, n = item[0], item[1], item[2]
    # The following loop is used for print all the k-v pairs
    # with the same k.
    k_li_rep_k_idx = 0
    rep_k_v = []
    ori_k_idx_inp = {}
    inp_ori_k_idx = {}

    for i in range(n):
        k_li_rep_k_idx = k_li.index(k, k_li_rep_k_idx)
        # print("The {0} key is: {1}, value is {2}"
        #       .format(str(i + 1), k_li[k_li_rep_k_idx], v_li[k_li_rep_k_idx]))
        rep_k_v.append(v_li[k_li_rep_k_idx])
        ori_k_idx_inp[k_li_rep_k_idx] = i + 1
        inp_ori_k_idx[i + 1] = k_li_rep_k_idx
        k_li_rep_k_idx += 1

    rep_k_v_set = set(rep_k_v)
    if rep_k_v_set == {""}:  # Repeated key only corresponds to "" value.
        inp = 1
    elif len(rep_k_v_set - {""}) == 1:  # Only 1 valid value to the rep key.
        v_idx = v_li.index(tuple(rep_k_v_set - {""})[0])  # Find the index
        # of the only valid value in the original pair-name/value list.
        inp = ori_k_idx_inp[v_idx]  # Find the 'inp' value corresponding to
        # this valid value index by the 'ori_k_idx_inp' dict.

    # The following part is for user to input a valid int number
    # to decide which of the repeat keys will be used. If the input is
    # invalid, the default key will be first one.
    if 1 <= inp <= 3:
        pass
    else:
        for i in range(n):
            try:
                print("There are duplicated label pairs as following:")
                print("-----" * 20, end="")
                for h in range(n):
                    print("\nThe {0} label-name is:\t{1}"
                          "\n\t  label-value is:\t{2}"
                          .format(str(h + 1), k_li[inp_ori_k_idx[h + 1]],
                                  v_li[inp_ori_k_idx[h + 1]]))
                print("-----" * 20)

                inp = int(input("Enter which one you want "
                                "(int number, like 1, 2, 3...):"))
                if inp < 1 or inp > n:
                    if i < n - 1:
                        print('invalid input, should only input int number '
                              'between 1 and %d, try again!'
                              '(remaining %d times, default the first one)'
                              % (n, (n - 1 - i)))
                        continue
                    else:
                        inp = 1
                else:
                    break
            except ValueError:
                print(
                    'invalid input, should only input int number '
                    'between 1 and %d, '
                    'try again! (remaining %d times, default the first one)'
                    % (n, (n - 1 - i)))
                if i == n - 1:
                    inp = 1
    del_po = [po + i for i in range(n) if i + 1 != inp]
    return del_po


def crawl_table(pq_doc, headers_css="", first_table_row_css="", cell_css="",
                seg_prefixes="", rearrange_table_method="numbering_headers",
                replace_string="", ignore_display_items=False,
                additional_table_rows_css=list(),
                prepared_table_headers=list(),
                prepared_table_data=list(), data_start=None, data_end=None):

    """crawl_table(pq_doc, headers_css, rows_css, seg_prefixes)
        -> <zip obj. of a dict>

    This function will read the data from:

       [h1      h2      h3      h4      h5      h6      ...]

       [r1_1    r1_2    r1_3    r1_4    r1_5    r1_6    ...]

       [r2_1    r2_2    r2_3    r2_4    r2_5    r2_6    ...]

       [r3_1    r3_2    r3_3    r3_4    r3_5    r3_6    ...]

       [...                                                ]

    And generate a 1D table as following:

     =>[h1_1    h1_2    h1_3  | h2_1    h2_2    h2_3  | ->
       [r1_1    r2_1    r3_1  | r1_2    r2_2    r3_2  |

     -> h3_1    h3_2    h3_3  | h4_1    h4_2    h4_3  | ->
        r1_3    r2_3    r3_3  | r1_4    r2_4    r3_4  |

     -> h5_1    h5_2    h5_3  | h6_1    h6_2    h6_3  | ...]
        r1_5    r2_5    r3_5  | r1_6    r2_6    r3_6  | ...]

    For headers, like h3_4, 3 means the third header, 4 means the forth rows,
    which corresponds to the data in cell of row 4 column 3 (r4, c3), as r4_3.

    After get the <zip obj. of table dict.>, it has to use the function of
    rearrange_table_numbering_headers(table) to generate the <tuple obj. of
    the final header_list - data_list>.

    :param:
    :seg_prefixes: For add the specific segment title in front of each keys,
        like "Sale" to "Sale_Sole Price, "Building" to "Building_Year Built",...
    :pq_doc: The PyQuery object of web-page source code.
    :headers_css: Css selector for table-headers.
    :rows_css: Css selector for each table-row's data.
    :cell_css: For further selection of the data in each row,
        usually it's <td>...</td>

    :return: A <zip obj.> for generating a dict as following:
        {
            'headers': <generator obj. of table-headers>,
            'rows': [[row_1 list], [row_2 list], ..., [row_n list]]
        }
    """

    if prepared_table_headers:
        table_headers = prepared_table_headers
    else:
        table_headers = crawl_table_headers(pq_doc, headers_css)

    if prepared_table_data:
        table_data = prepared_table_data
    else:
        table_data = crawl_table_data(pq_doc, ignore_display_items,
                                      first_table_row_css,
                                      additional_table_rows_css,
                                      cell_css, replace_string, data_start,
                                      data_end)

    table = dict(headers=table_headers, data=table_data)

    table_method = {
        'numbering_headers': rearrange_table_numbering_headers,
        'cross_headers': rearrange_table_cross_headers,
        'same_headers': rearrange_table_same_headers
    }
    t_h, t_d = table_method[rearrange_table_method](table, seg_prefixes)
    return t_h, t_d


def crawl_table_headers(pq_doc, headers_css):
    """Crawl the table headers as a <list obj.>"""
    return [h.text() for h in pq_doc(headers_css).items()]


def crawl_each_row(each_row_doc, cell_css, replace, start, end):
    """crawl_each_row(each_row_doc, cell_css, replace, start, end):
        -> <list obj. of each row's data>

    This function receives the css selectors of each row and data cell and
    return the data list.

    :param:
    :each_row_doc: <PyQuery obj.> of each row's source code.
    :cell_css: Data css selector for crawling each data in the row.
    :replace: Strings which needs to be replaced by "" (delete the useless
     characters in strings).
    :start: See in tool_funcs.row_filter().
    :end: See in tool_funcs.row_filter().

    :return: <list obj. of the crawled row>
    """
    each_row = [r.text().replace(replace, "").rstrip()
                for r in each_row_doc(cell_css).items()]
    if start or end:
        each_row = row_filter(each_row, start, end)
    return each_row


def crawl_table_data(pq_doc, ignore, main_rows_css, extra_rows_css_li,
                     cell_css, replace, start, end):
    """crawl_table_data(): -> <list obj. of data (per row)>

    This function is used to crawl the data of all rows in a list. For those
    tables which have two parts with different css selectors, for example,
    up table and bottom table with the same headers but different css selectors,
    all rows' css selectors need to be provided. If it's necessary to delete
    some data in the row, the 'start' and 'end' position also needs to be
    provided.

    :param:
    :pq_doc:  <PyQuery obj.> of web-page source code.
    :ignore: Bool value for determining whether needs the PyQuery nodes having
     attribute of '[style="display: none;"]'. True: -> delete the nodes; False:
     -> keep the nodes.
    :main_rows_css: The mainly (first) row's css selector.
    :extra_rows_css_li: The different rows' css selectors list.
    :cell_css: See in tool_funcs.crawl_each_row()
    :replace: See in tool_funcs.crawl_each_row()
    :start: See in tool_funcs.row_filter()
    :end: See in tool_funcs.row_filter()

    :return: Nested <list obj. of all rows> as following:
        [
            [data1_1, data1_2, data1_3, ...] # row 1 list
            [data2_1, data2_2, data2_3, ...] # row 2 list
            [data3_1, data3_2, data3_3, ...] # row 3 list
            ...
        ]
    """
    table_data = []
    rows_doc = pq_doc(main_rows_css)
    for extra in extra_rows_css_li:
        # Rows' css selectors of the same table may be different.
        extra_doc = pq_doc(extra)
        # Combine all rows PyQuery nodes as a final table row's PyQuery doc.
        rows_doc.extend(extra_doc)

    if ignore:
        rows_doc.remove_attr('[style="display: none;"]')
    for row in rows_doc.items():
        each_row = crawl_each_row(row, cell_css, replace, start, end)
        table_data.append(each_row)
    return table_data


def row_filter(data_per_row, row_start, row_end):
    """row_filter(data_per_row, row_start, row_end): -> <list obj. of data>

    This function is used to slice the data list (of each row) when it's
    necessary or not.

    :param:
    :data_per_row: <list of data> needs to be sliced.
    :row_start: The start position of the data list for filtering the useful
     data.
    :row_end: The end position of the data list for filtering the useful data.

    :return: The sliced <list obj. of data>
    """
    if row_start and row_end and (row_start < row_end):
        if row_start < 0:
            row_start = len(data_per_row) + row_start
        if row_end < 0:
            row_end = len(data_per_row) + row_end
    else:
        raise ValueError("expected: row_start > row_end")
    return data_per_row[row_start:row_end]


def rearrange_table_numbering_headers(table, pre_add):
    """rearrange_table_numbering_headers(table)
        -> <tuple obj. of headers and data>

    :param:
    :table: A table dict consists of two item, as following:
        table['header'] = A header list generator
        table['data'] = A nested list as:
                        [[row_1 list], [row_2 list], ..., [row_n list]]
    :t_h: The modified headers generator as
        <h1_1, h1_2, h1_3..., h2_1, h2_2, h2_3..., ..., hn_1, hn_2, hn_3...>,
        while, e.g., h2_3 means the second(2) header's the third(3) row's data
    :t_d: The 1-D data list is rearranged from the 2-D data list generated
        by the row list. The data is corresponding to the headers in <generator
        of the t_h list>

    :return: A <tuple obj.> consists of a table-header generator and an 1-D
        data iterator.
    """
    h = ["{0}_{1}".format(pre_add, item) for item in table['headers']]
    d = table['data']
    t_headers = [item + "_" + str(i + 1) for item in h for i in range(len(d))]
    # Switch flatten to ravel
    # t_data = list(numpy.array(d).flatten('F'))
    t_data = numpy.array(d).ravel('F').tolist()
    return t_headers, t_data


def rearrange_table_cross_headers(table, pre_add):
    """

    :param table:
    :param pre_add:
    :return:
    """
    up_headers = table['headers']
    left_headers = [row[0] for row in table['data']]

    t_headers = ("{0}_{1}_{2}_{3}".format(pre_add, up_headers[0], left_h, top_h)
                 if up_headers[0] != ""
                 else "{0}_{1}_{2}".format(pre_add, left_h, top_h)
                 for left_h in left_headers
                 for top_h in up_headers[1:])
    t_data = []
    for each_row in table['data']:
        t_data += each_row[1:]
    return t_headers, t_data


def rearrange_table_same_headers(table, pre_add):
    """

    :param table:
    :param pre_add:
    :return:
    """
    headers = table['headers']
    update_headers = [headers[0]
                      if i == 0
                      else "{0}_{1}".format(headers[0], h)
                      for i, h in enumerate(headers)]
    table['headers'] = update_headers
    t_h, t_d = rearrange_table_numbering_headers(table, pre_add)
    return t_h, t_d

# def rearrange_table_cross_headers(pq_doc, headers_css, cell_css, pre_add,
#                                   *row_css):
#     """rearrange_table_cross_headers(pq_doc, headers_css, pre_add, *row_css)
#         -> <zip obj. for a dict>
#
#         This function will read the data from:
#
#            [cro     up2     up3     up4     up5     up6      ...]
#
#            [le1     r1_2    r1_3    r1_4    r1_5    r1_6    ...]
#
#            [le2     r2_2    r2_3    r2_4    r2_5    r2_6    ...]
#
#            [le3     r3_2    r3_3    r3_4    r3_5    r3_6    ...]
#
#            [...                                                ]
#
#         And generate a 1-D table as following:
#
#          =>[c_le1_up2 | c_le1_up3 | c_le1_up4 | c_le1_up5 | c_le1_up6 ->
#            [r1_2        r1_3        r1_4        r1_5        r1_6
#
#          ->[c_le2_up2 | c_le2_up3 | c_le2_up4 | c_le2_up5 | c_le2_up6 ->
#            [r2_2        r2_3        r2_4        r2_5        r2_6
#
#          ->[c_le3_up2 | c_le3_up3 | c_le3_up4 | c_le3_up5 | c_le3_up6 ...]
#            [r3_2        r3_3        r3_4        r3_5        r3_6      ...]
#
#         All the 1-D table headers has to be add the segment name in front of
#         the headers, as 'segment name_c_le2_up5'.
#
#         :param:
#         :pre_add: For add the specific segment title in front of each keys,
#             like "Sale" to "Sale_Sole Price, "Building" to
#             "Building_Year Built",...
#         :pq_doc: The PyQuery object of web-page source code.
#         :headers_css: Css selector for table-headers.
#         :*rows_css: Variable css selectors for each table-row's data,
#             usually it's <td>...</td>. For those separate table with the same
#             headers, pass the css selectors of these 'separate' tables into
#             this function as following:
#              -> rearrange_table_cross_headers(pq_doc, headers_css, pre_add,
#                             row_css_1, row_css_2, row_css3, ...)
#         :cell_css: See in tool_funcs.py -> def crawl_table()
#
#         :return: A <tuple obj.> for generating a dict as following:
#             {
#                 'headers': [cross_left 1_top 1, cross_left 1_top 2 ,...
#                             cross_left 2_top 1, cross_left 2_top 2, ...
#                             cross_left 3_top 1, cross_left 3_top 2, ...]
#                 'data': [data_(1,1), data_(1,2), ...
#                          data_(2,1), data_(2,2), ...
#                          data_(3,1), data_(3,2), ...]
#                          which corresponds to the headers list
#             }
#         """
#     up_headers = [h.text() for h in pq_doc(headers_css).items()]
#     table_rows = []
#     for rc in row_css:
#         for row in pq_doc(rc).items():
#             # Because there would be some text that will not display in the
#             # files/webs, for example as "•\n" , so the .remove() is used to
#             # delete the text of this part.
#             row('[style="display: none;"]').remove()
#             table_rows.append([r.text().rstrip()
#                                for r in row(cell_css).items()])
#     left_headers = [row[0] for row in table_rows]
#
#     # Two cases as:
#     # 1. the table has the cross header:
#     #                       segment name_cross header_left header_up header
#     # 2. cross header is "": Demographics_Population_1 Mi
#     #                        segment name_left header_up header
#     table_headers = ["{0}_{1}_{2}_{3}"
#                      .format(pre_add, up_headers[0], left_h, top_h)
#                      if up_headers[0] != ""
#                      else "{0}_{1}_{2}".format(pre_add, left_h, top_h)
#                      for left_h in left_headers
#                      for top_h in up_headers[1:]]
#
#     table_data = []
#     for r in table_rows:
#         table_data += r[1:]
#     # Check whether the 1-D table's key-value could be matched.
#     assert len(table_headers) == len(table_data), \
#         "module tool_funcs.py -> def rearrange_table_cross_headers(): " \
#         "table headers and data doesn't match"
#     return table_headers, table_data


# def rearrange_table_same_headers(table, pre_add):
#     """
#
#     :param pq_doc:
#     :param headers_css:
#     :param cell_css:
#     :param pre_add:
#     :param row_css:
#     :return:
#     """
#     ori_headers = [item.text() for item in pq_doc(headers_css).items()]
#     table_headers = [pre_add + "_" + ori_headers[i]
#                      if i == 0
#                      else pre_add + "_" + ori_headers[0] + "_" + ori_headers[i]
#                      for i in range(len(ori_headers))]
#     table_data = []
#     for rc in row_css:
#         for row in pq_doc(rc).items():
#             table_data.append([r.text().rstrip()
#                                for r in row(cell_css).items()])
#
#     print('!!!!!!!!!!!1')
#     print(table_headers)
#     print(table_data)
#     print("@@@@@@@@@@@@@@@@")
#
#     return zip(['headers', 'data'], [table_headers, table_data])
