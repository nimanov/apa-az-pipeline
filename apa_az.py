import time
import datetime
import psycopg2
import psycopg2.extras
from psycopg2 import errors
from psycopg2.errorcodes import UNIQUE_VIOLATION
from utils import request_handler, could_not_scraped


def sub_categories(category, category_name):
    hostname = '172.18.0.2'
    database = 'neurotime'
    username = 'nurlan'
    pwd = 1234
    port_id = 5432
    conn = None
    for sub_ctgry in category.find("ul").find_all("li"):
        news_date_is_2023 = True
        soup_first_page = request_handler(sub_ctgry.a["href"] + "?page=1", 10, 60)
        if soup_first_page == "NOT RESPONDING":
            could_not_scraped(sub_ctgry)
            continue
        try:
            page_num = int(soup_first_page.find(class_="pagination").find_all("li")[-2].a.text)
        except AttributeError:
            page_num = 2
        for page_index in range(1, page_num):
            sub_ctgry_page_url = sub_ctgry.a["href"] + "?page=" + str(page_index)
            soup_sub_ctgry = request_handler(sub_ctgry_page_url, 10, 60)
            if soup_sub_ctgry == "NOT RESPONDING":
                could_not_scraped(sub_ctgry_page_url)
                continue
            news_category = sub_ctgry.a.text + "(" + category_name + ")"
            already_scraped = 0
            number_of_news_in_page = 0
            for page_news in soup_sub_ctgry.find(class_="four_columns_block mt-site").find_all("a"):

                number_of_news_in_page += 1
                url_of_news = page_news["href"]
                if "javascript" in url_of_news:
                    # Paid news
                    continue
                content = ""
                tags = ""
                index = -1
                soup_news = request_handler(url_of_news, 10, 60)
                if soup_news == "NOT RESPONDING":
                    could_not_scraped(url_of_news)
                    continue

                date = soup_news.find(class_="date").span.text
                if "2023" not in date:
                    news_date_is_2023 = False
                    break
                title = soup_news.find(class_="title_news mb-site").text
                author = soup_news.find(class_="tags mt-site").span.text
                if author.strip().lower() == "apa": author = None
                img_link = soup_news.find(class_="main_img").img["src"]
                number_of_p = len(soup_news.find(class_="texts mb-site").find_all("p"))

                for p in soup_news.find(class_="texts mb-site").find_all("p"):
                    index += 1
                    if p.strong and (index == number_of_p - 1) and len(p.strong.text.split()) == 2:
                        if author==None:
                            author = p.strong.text
                            continue
                    content += p.text.strip() + " "
                if soup_news.find(class_="tags mt-site") != None:
                    for a in soup_news.find(class_="tags mt-site").find(class_="links").find_all("a"):
                        tags += a.text.strip() + ", "
                tags = tags.strip().strip(",")
                if len(tags) == 0: tags = None
                scraped_date = str(datetime.datetime.now())
                try:
                    with psycopg2.connect(
                            host=hostname,
                            dbname=database,
                            user=username,
                            password=pwd,
                            port=port_id) as conn:

                        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                            create_script = ''' CREATE TABLE IF NOT EXISTS apa_az (
                                                    id      BIGSERIAL NOT NULL PRIMARY KEY,
                                                    url     VARCHAR UNIQUE,
                                                    title     VARCHAR ,
                                                    date     VARCHAR ,
                                                    img_link     VARCHAR ,
                                                    content     VARCHAR ,
                                                    category     VARCHAR ,
                                                    author     VARCHAR ,
                                                    tags     VARCHAR,
                                                    scraped_date VARCHAR)
                                                    '''
                            cur.execute(create_script)
                            insert_script = '''INSERT INTO apa_az 
                                                (url, title, date, img_link, content, 
                                                category, author, tags, scraped_date) 
                                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                             '''
                            record = (url_of_news.strip(), title.strip(), date,
                                      img_link, content.strip(), news_category, author, tags, scraped_date,)
                            cur.execute(insert_script, record)
                            print("Written to database", str(datetime.datetime.now()), news_category, url_of_news)
                except errors.lookup(UNIQUE_VIOLATION):  # Means this url already scraped
                    already_scraped += 1
                    continue
                except Exception as error:

                    f_error_log = open("error.log", "a", encoding="utf-8")
                    msg = "DATABASE ERROR " + str(datetime.datetime.now()) + " "
                    f_error_log.write(msg + " ==> " + str(error) + "\n")
                    f_error_log.close()
                    return -1
                finally:
                    if conn is not None:
                        conn.close()

            if not news_date_is_2023 or number_of_news_in_page == already_scraped:
                break

    return 1


def main_categories(soup):
    # Go through each main category
    for category in soup.find_all(class_="link_block"):
        # Taking each main category name
        category_name = category.h3.text.replace("I", "ı").replace("İ", "i").lower()
        if category_name not in ["apa tv", "təhlil", "bloqlar", "şirkət", "top 10", "arxiv"]:
            return_value = sub_categories(category, category_name)
            if return_value == -1:
                return -1
    return 1


def apa_scraper():
    apa_az_url = "https://apa.az/az/all-news"  # The page that shows all main categories
    soup = request_handler(apa_az_url, 10, 60)
    if soup == "NOT RESPONDING":
        could_not_scraped(apa_az_url)
        return
    main_categories(soup)


while True:
    apa_scraper()
    print("Finished the cycle", str(datetime.datetime.now()))
    time.sleep(3600)
