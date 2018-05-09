import MySQLdb

from scrapy.exceptions import NotConfigured


class LawNewsPipeline(object):
    def process_item(self, item, spider):
        return item


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
            "INSERT INTO news (headlines,published_date,image,brief,news_html)"
            "VALUES (%s,%s,%s,%s,%s)")
        t = (item["headlines"], item["published_date"], item["image"], item["brief"],item["news_html"])
        self.cursor.execute(query, t)
        self.conn.commit()
        return item
