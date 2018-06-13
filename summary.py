# from pyquery import PyQuery as pq
import sys
import tool_funcs
import id_add
# from decorator import pairs
import decorator


class Summary(object):
    """
    This class is used for crawling data in Summary page.
    For other pages with the same structure as Summary, like Comps,
    this class could also be used.

    This class will receive the source code to initialize the PyQuery object.

    If the data in the only one of these segments is to used, like 'Sale',
    it could be get by the corresponding instance method, for example,
    if I only need the data in 'Sale', step as following:
        1. initialize the class, s = Summary(pq_doc)
        2. get the specified segment attribute, s.sale(), it will return a dict
        generator of the data, result_generator = s.sale()
        3. get the data from the generator by result = dict(result_generator)

    Modify the class:
        If there are some new segments appearing in the Summary page which
        needs to be crawled, the following step needs to be following to add
        the segment into class:
            1. build new class method -> def new_seg(self):
            2. add a new key-value, which value is the function pointer
            without parentheses '()', as following:

                self.all_title_methods = {
                    ...
                    'New Title From the File/Web-page': self.new_seg
                }
    """

    def __init__(self, pq_doc, web_id):
        # The type of 'pq_doc' is PyQuery object.
        self._pq_doc = pq_doc
        self._id = id_add.ID(web_id)
        self.result = {}
        self.titles_in_web = self.crawl_titles_in_web('Documents',
                                                      'Building Notes')
        self.all_titles_methods = {
            'Sale': self.sale,
            'Building': self.building,
            'Land': self.land,
            'Location': self.location,
            'Property Contacts': self.property_contacts,
            'For Lease': self.for_lease,
            'Amenities': self.amenities,
            'Traffic': self.traffic,
            'Tenants': self.tenants,
            'Unit Mix': self.unit_mix,
            'Demographics': self.demographics,
            'Assessment': self.assessment,
            'Market Conditions': self.market_conditions,
            'Public Transportation': self.public_transportation,
            'Space': self.space,
            'Leasing Activity': self.leasing_activity
        }
        self.run_crawl()
        self._address = id_add.address(pq_doc)
        self.result.update(self._id)
        self.result.update(self._address)

    def run_crawl(self):
        print(">>>>>>>>>>>>>>>")
        print('Running Summary...')
        print('External titles are:\n\t', self.titles_in_web)
        print("Remaining segments are:\n\t", set(self.titles_in_web) -
              set(self.all_titles_methods.keys()))
        try:
            for seg in self.titles_in_web:
                self.result.update(dict(self.all_titles_methods[seg]()))

        # 下面except语句以后可以修改为写入日志，这里先正常报错以便写完程序
        except KeyError as ke:
            print(">>> Warning: There is no '{0}' method in the class Summary, "
                  "this file/web-page's crawling will be ignored, please add "
                  "the {0} method in the class, after that rerun the code."
                  .format(ke))
            raise ke

    def crawl_titles_in_web(self, *ignore_titles):
        """crawl_titles_in_web(self) -> list generator

        This method is used to get all segments titles for determine which
        method will be used to crawl data. If no ignored title pass, then
        the 'if' and 'for' statement for deleting the ignored titles won't be
        executed. If only one ignored title pass to the method, only the 'if'
        will be executed. The 'for' statement will only affect those files/webs
        which needs to ignore more than one segment.

        :param:
        :*ig_titles: Variable (zero or more) ignored titles needs to be deleted.

        :return: segments titles list generator
        """
        css_selector = '#content h1'
        titles = [item.text() for item in self._pq_doc(css_selector).items()]

        # Delete the first ignored title, if default (None), jump out of 'if'
        # and 'for' statement.

        for ig_t in ignore_titles:
            if ig_t in titles:
                titles.remove(ig_t)
        return titles

    def sale(self):
        css_selector = "[data-viewmodelname='propertySale']"
        # _sale is a dict generator
        _sale = tool_funcs.pairs_gene(self._pq_doc, css_selector, 'Sale')
        return _sale

    def building(self):
        css_selector = '[data-viewmodelname="propertyBuildingInformation"]'

        add_name = []
        add_value = []
        # For judging whether there is 'Walk Score' in Building segment.
        if self._pq_doc('[data-bind="attr: { href: WalkScoreHelpLink }"]'):
            name = self._pq_doc('[data-bind='
                                '"attr: { href: WalkScoreHelpLink }"]').text()
            add_name.append(name)
            value = self._pq_doc('[data-bind='
                                 '"text: FormattedWalkScore"]').text()
            add_value.append(value)

        # For judging whether there is 'Transit Score' in Building segment.
        if self._pq_doc('[data-bind="attr: { href: TransitScoreHelpLink }"]'):
            name = self._pq_doc('[data-bind="attr: '
                                '{ href: TransitScoreHelpLink }"]').text()
            add_name.append(name)
            value = self._pq_doc('[data-bind='
                                 '"text: FormattedTransitScore"]').text()
            add_value.append(value)

        _building = tool_funcs.pairs_gene(self._pq_doc, css_selector,
                                          'Building', add_name, add_value)
        return _building

    def land(self):
        css_selector = '[data-viewmodelname="propertyLand"]'
        _land = tool_funcs.pairs_gene(self._pq_doc, css_selector, 'Land')
        return _land

    def location(self):
        css_selector = '.property-location'
        _location = tool_funcs.pairs_gene(self._pq_doc, css_selector,
                                          ' Location')
        return _location

    def property_contacts(self):
        css_selector = '.property-contacts'
        _property_contacts = tool_funcs.pairs_gene(self._pq_doc, css_selector,
                                                   'Property Contacts')
        return _property_contacts

    def for_lease(self):
        css_selector = '[data-viewmodelname="propertyForLease"]'
        # inp is the choice of the repeated key-value pair.
        _for_lease = tool_funcs.pairs_gene(self._pq_doc, css_selector,
                                           'For Lease', inp=1)
        return _for_lease

    def amenities(self):
        """This segment usually includes tow parts, 'Unit Amenities' and
        'Site Amenities'. Each part contains several amenities. To list all of
        these stuff, a comma ',' will be used to separate these stuff.

        :param:
        :amen_subtitles: Subsections of the Amenities segment, usually contains
            two subsections, 'Unit Amenities' and 'Site Amenities'.
        :value_li: The corresponding stuff to each subsection.

        :return: An amenities zip object (an object of combination of
            several tuples)
        """
        amen_subtitles = [item.text()
                          for item in self._pq_doc('.amenities-header').items()]
        value_css_selector_li = [".{0} {1}".format(
            item.lower().replace(' ', '-'), '.amenities-content')
            for item in amen_subtitles]
        value_li = [self._pq_doc(css).text().replace('\n', ', ')
                    for css in value_css_selector_li]
        _amenities = zip(amen_subtitles, value_li)
        return _amenities

    def traffic(self):
        """traffic(self) -> <zip obj. of (list, list)>

        The Traffic segments contains a table with a row of table-header and
        several data rows.

        :param:
        :table: See in tool_funcs.py
            -> def rearrange_table_numbering_headers(table)
        :t_h: See in tool_funcs.py
            -> def rearrange_table_numbering_headers(table)
        :t_d: See in tool_funcs.py
            -> def rearrange_table_numbering_headers(table)

        :return: A <zip obj.> consists of the
            <generator obj. of table_headers> and <iterator obj. of table_rows>
        """
        headers_css_selector = '#TrafficTable thead th'
        row_css_selector = '#TrafficTable tbody tr'
        cell_css_selector = 'td'
        t_h, t_d = tool_funcs.crawl_table(
            self._pq_doc, headers_css_selector,
            row_css_selector, cell_css_selector,
            'Traffic', 'numbering_headers'
        )
        return zip(t_h, t_d)

    def tenants(self):
        headers_css_selector = '#TenantsTable thead th'
        row_css_selector = '#TenantsTable tbody tr'
        cell_css_selector = 'td'
        t_h, t_d = tool_funcs.crawl_table(
            self._pq_doc, headers_css_selector,
            row_css_selector, cell_css_selector,
            'Tenants', 'numbering_headers',
            replace_string="•\n"
        )
        return zip(t_h, t_d)

    def unit_mix(self):
        headers_css_selector = '#UnitMixTable thead th'
        row_css_selector = '#UnitMixTable tbody tr'
        cell_css_selector = 'td'
        t_h, t_d = tool_funcs.crawl_table(
            self._pq_doc, headers_css_selector,
            row_css_selector, cell_css_selector,
            'Unit Mix', 'numbering_headers'
        )
        return zip(t_h, t_d)

    def demographics(self):
        headers_css_selector = '#DemogrpahicsTable thead th'
        top_row_css_selector = '#DemogrpahicsTable tbody tr'
        bot_row_css_selector = '#DemogrpahicsTrendTable tbody tr'
        cell_css_selector = 'td'

        t_h, t_d = tool_funcs.crawl_table(
            self._pq_doc, headers_css_selector,
            top_row_css_selector, cell_css_selector,
            'Demographics', 'cross_headers',
            ignore_display_items=False,
            additional_table_rows_css=[bot_row_css_selector]
        )
        return zip(t_h, t_d)

    def assessment(self):
        year_css_selector = "#assesmentInformationContainer " \
                            "[data-bind='if: showAssessedYear()'] span"
        year = self._pq_doc(year_css_selector).text()
        if year:
            seg_prefixes = 'Assessment_{0} Assessment'.format(year)
        else:
            seg_prefixes = 'Assessment'

        headers_css_selector = '#assesmentInformationContainer .subheader'
        row_css_selector = '#assesmentInformationContainer .column'
        cell_selector = '.row'

        crawl_data = []
        for r in self._pq_doc(row_css_selector).items():
            crawl_data.append([item.text() for item in r(".row").items()][1:])
        crawl_data = crawl_data[1:]

        t_h, t_d = tool_funcs.crawl_table(
            self._pq_doc, headers_css=headers_css_selector,
            prepared_table_data=crawl_data,
            cell_css=cell_selector,
            seg_prefixes=seg_prefixes,
            rearrange_table_method='numbering_headers',
            data_start=1
        )
        return zip(t_h, t_d)

    def market_conditions(self):
        """market_conditions(self) -> <zip obj. of (list, list)>

        The segment of Market Conditions have two main parts, one for
        sub-table (top tables) with headers of 'Current' and 'YOY Change',
        the other (bot table) with headers of 'Current' and 'Prev Year'.

        In this part, all headers of each sub-table needs to be updated as
        desired. So the headers are crawled before passing the headers css into
        the tool_funcs.crawl_table function.

        ":param:
        :segments: The segments names list contained in the 'Market Conditions'
            part.
        :up_headers: Usually are 'Current' and 'YOY Change'
        :bot_heades: Usually are 'Current' and 'Prev Year'
        :segments_data_bind_css: This css is used to locate the data which
            needs to be crawled in each segment. It's a <dict. obj.>
            corresponding to the segments names.
        :t_h, t_d: The final 1-D headers list and 1-D data list for generating
            the <zip obj.>

        :return: <zip obj. of the 1-D headers and data>
        """
        segments_css_selectors = '.property-marketConditions h4'
        segments = [item.text()
                    for item in self._pq_doc(segments_css_selectors).items()]
        up_headers_css_selectors = '.property-marketConditions ' \
                                   '.section-header.column'
        up_headers = [item.text()
                      for item
                      in self._pq_doc(up_headers_css_selectors).items()]
        bot_headers_css_selectors = '.property-marketConditions ' \
                                    '.headerLabel'
        bot_headers = [item.text()
                       for item
                       in self._pq_doc(bot_headers_css_selectors).items()]

        segments_data_bind_css = {
            'Submarket Leasing Activity':
                '[data-bind="visible: hasTwelveMonthActivity"]',
            'Asking Rents Per SF': '[data-bind="visible: hasAskingRent"]',
            'Asking Rents Per Unit': '[data-bind="visible: hasAskingRent"]',
            'Gross Asking Rents Per SF': '[data-bind="visible: hasAskingRent"]',
            'NNN Asking Rents Per SF': '[data-bind="visible: hasAskingRent"]',
            'Same Store Asking Rent Per Unit':
                '[data-bind="visible: hasAskingRent"]',
            'Same Store Asking Rent Per SF':
                '[data-bind="visible: hasAskingRent"]',
            'Concessions': '[data-bind="visible: hasConcessions"]',
            'Under Construction Units':
                '[data-bind="visible: hasConstructionUnits"]',
            'Submarket Sales Activity':
                '[data-bind="visible: hasSalesActivity"]',
            'Vacancy Rates': '[data-bind="visible: hasVacancyRate"]'
        }
        t_h = []
        t_d = []
        for seg in segments:
            data_css_selector = segments_data_bind_css[seg] + " .table-row"
            # Only the last segment has the headers of 'Current' and 'Prev Year'
            if seg != segments[-1]:
                # The first several sub-tables.
                seg_headers = [seg] + up_headers
                seg_data = [
                    item.text().split('\n')
                    for item in self._pq_doc(data_css_selector).items()
                ]
            else:
                # The last sub-table, which has a different table structure.
                seg_headers = [seg] + bot_headers
                seg_data = [
                    item.text().split('\n')
                    for item in self._pq_doc(data_css_selector).items()
                ][1:]
            # seg_t_h, seg_t_d corresponds to each sub-table's headers and data.
            seg_t_h, seg_t_d = tool_funcs.crawl_table(
                self._pq_doc,
                seg_prefixes='Market Conditions',
                prepared_table_headers=seg_headers,
                prepared_table_data=seg_data,
                rearrange_table_method='cross_headers'
            )
            # Join all sub-table's 1-D headers and data in to the final lists.
            t_h += seg_t_h
            t_d += seg_t_d
        return zip(t_h, t_d)

    def public_transportation(self):
        """public_transportation(self) -> <zip obj. of (list, list)>

        This part usually has at most three sub-tables, which are 'Airport',
        'Commuter Rail' and 'Transit/Subway'. Therefore, all there three
        sub-tables' headers-css and rows-css are put in a list and then passed
        to the tool_funcs.crawl_table() function.

        :return: <zip obj. of the 1-D headers and data>
        """
        headers_css_selectors = [
            ".public-transportation-layout "
            "[data-bind='visible: hasSubways'] .head .column",

            ".public-transportation-layout "
            "[data-bind='visible: hasCommuterRail'] .head .column",

            ".public-transportation-layout "
            "[data-bind='visible: hasAirports'] .head .column"
        ]

        rows_css_selectors = [
            ".public-transportation-layout "
            "[data-bind='visible: hasSubways'] "
            "[data-bind='foreach: data.Items'] .row",

            ".public-transportation-layout "
            "[data-bind='visible: hasCommuterRail'] "
            "[data-bind='foreach: data.Items'] .row",

            ".public-transportation-layout "
            "[data-bind='visible: hasAirports'] "
            "[data-bind='foreach: data.Items'] .row"
        ]
        cell_css_selector = '.column'

        t_h = []
        t_d = []
        for i, h_css in enumerate(headers_css_selectors):
            each_t_h, each_t_d = tool_funcs.crawl_table(
                self._pq_doc,
                h_css,
                rows_css_selectors[i],
                cell_css_selector,
                'Public Transportation',
                'same_headers'
            )
            t_h += each_t_h
            t_d += each_t_d
        return zip(t_h, t_d)

    def space(self):
        headers_css_selector = "[data-viewmodelname='propertySpaces'] thead th"
        row_css_selector = "[data-viewmodelname='propertySpaces'] tbody tr"
        cell_css_selector = 'td'
        t_h, t_d = tool_funcs.crawl_table(
            self._pq_doc, headers_css_selector,
            row_css_selector, cell_css_selector,
            'Space', 'numbering_headers'
        )
        return zip(t_h, t_d)

    def leasing_activity(self):
        headers_css_selector = "#LeasingActivityTable thead th"
        row_css_selector = "#LeasingActivityTable tbody tr"
        cell_css_selector = 'td'
        t_h, t_d = tool_funcs.crawl_table(
            self._pq_doc, headers_css_selector,
            row_css_selector, cell_css_selector,
            'Leasing Activity', 'numbering_headers'
        )
        return zip(t_h, t_d)
