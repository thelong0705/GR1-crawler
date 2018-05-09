import MySQLdb
import time
import datetime
from scrapy.exceptions import NotConfigured


class LawCrawlerPipeline(object):
    def process_item(self, item, spider):
        for k, v in item.items():
            item[k] = self.clean_field(v)
        item['ngay_ban_hanh'] = self.clean_date(item.get('ngay_ban_hanh',None))
        item['ngay_co_hieu_luc'] = self.clean_date(item.get('ngay_co_hieu_luc',None))
        item['ngay_dang_cong_bao'] = self.clean_date(item.get('ngay_dang_cong_bao',None))
        item['ngay_het_hieu_luc'] = self.clean_date(item.get('ngay_het_hieu_luc',None))

        return item

    def clean_date(self, string):
        try:
            return int(time.mktime(datetime.datetime.strptime(string, "%d/%m/%Y").timetuple()))
        except:
            return None

    def clean_field(self,string):
        if string and string.strip():
            return string
        return None

class DatabasePipeline(object):
    def __init__(self, db, user, passwd, host):
        self.conn = MySQLdb.connect(db=db,
                                    user=user,
                                    passwd=passwd,
                                    host=host,
                                    charset='utf8',
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise NotConfigured
        db = db_settings['db']
        user = db_settings['user']
        passwd = db_settings['passwd']
        host = db_settings['host']
        return cls(db, user, passwd, host)

    def process_item(self, item, spider):
        query = (
            "INSERT INTO van_ban_phap_luat (so_ky_hieu,ngay_het_hieu_luc,"
            "co_quan_ban_hanh,nguon_thu_thap,trich_yeu,ngay_dang_cong_bao,"
            "thong_tin_ap_dung,phan_loai,nguoi_ky,pham_vi,ly_do_het_hieu_luc,link_to_file,"
            "ngay_co_hieu_luc,ngay_ban_hanh,tinh_trang_hieu_luc)"
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        t = ([item.get('so_ky_hieu', None)],
             [item.get("ngay_het_hieu_luc", None)],
             [item.get("co_quan_ban_hanh", None)],
             [item.get("nguon_thu_thap", None)],
             [item.get("trich_yeu", None)],
             [item.get("ngay_dang_cong_bao", None)],
             [item.get("thong_tin_ap_dung", None)],
             [item.get("phan_loai", None)],
             [item.get("nguoi_ky", None)],
             [item.get("pham_vi", None)],
             [item.get("ly_do_het_hieu_luc", None)],
             [item.get("link_to_file", None)],
             [item.get("ngay_co_hieu_luc", None)],
             [item.get("ngay_ban_hanh", None)],
             [item.get("tinh_trang_hieu_luc", None)]
             )
        self.cursor.execute(query, t)
        self.conn.commit()
        return item
