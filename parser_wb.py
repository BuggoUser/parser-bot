import requests
import sqlite3

headers = {
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9',
        'origin': 'https://www.wildberries.ru',
        'priority': 'u=1, i',
        'referer': 'https://www.wildberries.ru/brands/fanbox',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "YaBrowser";v="25.8", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36',
        'x-pow': '',
    }

params = {
        'ab_testing': 'false',
        'appType': '1',
        'brand': '636249',
        'curr': 'rub',
        'dest': '123585487',
        'lang': 'ru',
        'page': '1',
        'sort': 'newly',
        'spp': '30',
        'limit' : '300'
    }


db, c = None, None

def start_db():
    global db, c
    db = sqlite3.connect('parser_wb.db')
    c = db.cursor()

def close_db():
    global db, c
    db.close()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS main_data (id INTEGER PRIMARY KEY, name_product VARCHAR(128) NOT NULL, price INTEGER NOT NULL, 
    article INTEGER NOT NULL UNIQUE, link TEXT NOT NULL)''')
    db.commit()

def get_data_from_db():
    c.execute('''SELECT * FROM main_data''')
    get_data = c.fetchall()
    return get_data

def get_price_from_db():
    all_price = c.execute('''SELECT price, article FROM main_data''').fetchall()
    return all_price

def get_article_from_db():
    c.execute('''SELECT article FROM main_data''')
    get_data_article = c.fetchall()
    return get_data_article

def update_price(new_price):
    res = []
    for i in new_price:
        res.append((i[0][1], i[0][2]))

    for i in res:
        c.execute('''UPDATE main_data SET price = ? WHERE article = ?''', (i[0], i[1]))
        db.commit()

def insert_data_to_db(list_data):
    c.executemany('''INSERT OR IGNORE INTO main_data (name_product, price, article, link) VALUES (?, ?, ?, ?)''', list_data)
    db.commit()
    print('Данные добавлены в функции insert_data_to_db')

def data_for_user_price(price):
    insert_data_and_validate()
    c.execute('''SELECT name_product, price, article, link FROM main_data WHERE price = ?''', (price,))
    all_price = c.fetchall()
    return all_price

def parser():
    all_products = []

    try:
        response = requests.get('https://catalog.wb.ru/brands/v4/catalog', params=params, headers=headers).json()
        for i in response.get('products'):
            name = i.get('name')
            price = str(i.get('sizes')[0].get('price').get('product'))[:-2]
            article = i.get('id')
            link = 'https://www.wildberries.ru/catalog/' + str(article) + '/detail.aspx'

            all_products.append((name, price, article, link))

        return all_products
    except Exception as e:
        print(e)

def check_new_price():
    sale_for_product = []
    set_data = parser()
    save_price = get_price_from_db()

    for p in set_data:
        for s in save_price:
            if p[2] == s[1]:
                if int(p[1]) != s[0]:
                    print('Скидка')
                    sale_for_product.append((p, s[0]))
                else:
                    print('Цена не изменилась')
    update_price(sale_for_product)
    return sale_for_product

def insert_data_and_validate():
    """Получаю список из кортежей"""
    set_data = parser()
    article = set(i[0] for i in get_article_from_db())

    data_for_insert = []
    data_for_check = []

    for p in set_data:
        current_article = p[2]
        if current_article not in article:
            data_for_check.append(p)
            data_for_insert.append(p)

    if data_for_insert:
        insert_data_to_db(data_for_insert)
        print('Данные вставлены')
        return data_for_check
    else:
        return None


if __name__ == '__main__':
    start_db()
    insert_data_and_validate()
    close_db()