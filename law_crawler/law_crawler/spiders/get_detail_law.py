import scrapy
from functools import partial


class LawDetailSpider(scrapy.Spider):
    name = "law_detail"
    law_url = 'http://www2.vanban.chinhphu.vn/portal/page/portal/chinhphu/hethongvanban'
    find_url = 'http://vbpl.vn/VBQPPL_UserControls/Publishing_22/TimKiem/p_KetQuaTimKiemVanBan.aspx??type=0&s=1' \
               '&SearchIn=Title&IsVietNamese=True&RowPerPage=50&Keyword='
    page = 1
    number_of_pages = 0

    dictionary = {
        'Số/Ký hiệu':'so_ky_hieu',
        'Ngày ban hành':'ngay_ban_hanh',
        'Ngày có hiệu lực':'ngay_co_hieu_luc',
        'Người ký':'nguoi_ky',
        'Trích yếu':'trich_yeu',
        'Cơ quan ban hành':'co_quan_ban_hanh',
        'Phân loại': 'phan_loai'
    }

    def start_requests(self):
        data = {
            'category_id': '8',
            'pagesize': '200',
            '_page': str(self.page)
        }
        yield scrapy.FormRequest(url=self.law_url, formdata=data, callback=self.parse)

    def parse(self, response):
        first_link = response.css('tr.doc_list_title_row+tr').css("a.doc_list_link::attr(href)").extract_first()
        yield response.follow(first_link, self.parse_detail)
        for row in response.css('tr.doc_list_row'):
            link = row.css("a.doc_list_link::attr(href)").extract_first()
            yield response.follow(link, self.parse_detail)
        for row in response.css('tr.doc_list_row+tr'):
            link = row.css("a.doc_list_link::attr(href)").extract_first()
            yield response.follow(link, self.parse_detail)
        if self.number_of_pages == 0:
            self.number_of_pages = int(response.css('select#d_page_id').css('option:last-child::text').extract_first())
        self.page += 1
        if self.page <= self.number_of_pages:
            data = {
                'category_id': '8',
                'pagesize': '200',
                '_page': str(self.page)
            }
            yield scrapy.FormRequest(url=self.law_url, formdata=data, callback=self.parse)

    def parse_detail(self, response):
        rows = response.css("div.doc_detail_attr_div tr td::text")
        details_dict = {}
        for i in range(0, len(rows) - 1, 2):
            k = rows[i].extract().strip()
            v = rows[i + 1].extract().strip()
            try:
                details_dict[self.dictionary[k]] = v
            except KeyError:
                details_dict['so_ky_hieu'] = None
                details_dict['ngay_ban_hanh'] = rows[2].extract().strip()
                details_dict['nguoi_ky'] = rows[4].extract().strip()
                details_dict['trich_yeu'] = rows[6].extract().strip()
                details_dict['co_quan_ban_hanh'] = rows[8].extract().strip()
                details_dict['phan_loai'] = rows[10].extract().strip()
                break

        details_dict['link_to_file'] = response.css('table.doc_detail_file a::attr(href)').extract_first()
        yield response.follow(url=self.find_url + rows[1].extract().strip(),
                              callback=partial(self.search_in_vbpl, details_dict=details_dict),
                              dont_filter=True)

    def search_in_vbpl(self, response, details_dict):
        list_url = response.css("li.thuoctinh a::attr(href)")
        list_ngay_ban_hanh = response.css("p.green:nth-child(1)")
        url_result = ''
        if len(list_url) > 0:
            for i in range(len(list_url)):
                if list_ngay_ban_hanh[i].css("::text")[-1].extract().strip() == details_dict['ngay_ban_hanh']:
                    url_result = list_url[i].extract()
                    break
        if url_result != '':
            yield response.follow(url=url_result,
                                  callback=partial(self.get_detail_vbpl, details_dict=details_dict),
                                  dont_filter=True)
        else:
            if 'ngay_co_hieu_luc' not in details_dict:
                details_dict['ngay_co_hieu_luc'] = None
            details_dict['nguon_thu_thap'] = None
            details_dict['ngay_dang_cong_bao'] = None
            details_dict['pham_vi'] = None
            details_dict['thong_tin_ap_dung'] = None
            details_dict['tinh_trang_hieu_luc'] = None
            details_dict['ly_do_het_hieu_luc'] = None
            details_dict['ngay_het_hieu_luc'] = None
            yield details_dict

    def get_detail_vbpl(self, response, details_dict):
        list_td = response.css("div.vbProperties td")
        if 'ngay_co_hieu_luc' not in details_dict:
            details_dict['ngay_co_hieu_luc'] = self.get_info(list_td, 'Ngày có hiệu lực')
        details_dict['nguon_thu_thap'] = self.get_info(list_td, 'Nguồn thu thập')
        details_dict['ngay_dang_cong_bao'] = self.get_info(list_td, 'Ngày đăng công báo')
        details_dict['pham_vi'] = self.get_info(list_td, 'Phạm vi')
        details_dict['thong_tin_ap_dung'] = self.get_info(list_td, 'Thông tin áp dụng')
        details_dict['tinh_trang_hieu_luc'] = response.css("div.vbInfo ul li.red::text")[-1].extract().strip()
        details_dict['ly_do_het_hieu_luc'] = self.get_info(list_td, 'Lí do hết hiệu lực')
        details_dict['ngay_het_hieu_luc'] = self.get_info(list_td, 'Ngày hết hiệu lực')
        yield details_dict

    def get_info(self, list_td, query):
        for i in range(len(list_td)):
            if query == 'Thông tin áp dụng' and list_td[i].css("p strong::text").extract_first() is not None:
                if list_td[i].css("p strong::text").extract_first().strip() == query:
                    return list_td[i].css("::text")[-1].extract().strip()
            if list_td[i].css("::text").extract_first().strip() == query:
                if query == 'Phạm vi':
                    result = list_td[i + 1].css("li::text").extract_first()
                    if result is not None:
                        return result.strip()
                return list_td[i + 1].css("::text").extract_first().strip()
        return None
