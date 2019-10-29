from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError,IntegrityError
import base64
import string, sqlite3
from urllib.parse import urlparse

host = 'http://localhost:5000/'

def table_check():
    create_table = """
        CREATE TABLE WEB_URL(ID INT PRIMARY KEY AUTOINCREMENT,URL TEXT NOT NULL);
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass

# Base62 Encoder and Decoder
def encoding(num, b = 62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + string.ascii_lowercase + string.ascii_uppercase 
    r = num % b
    res = base[r];
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res

def decoding(num, b = 62):
    base = string.digits + string.ascii_lowercase + string.ascii_uppercase 
    limit = len(num)
    res = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res


app = Flask(__name__)

# Home page where user should enter 
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form.get('url')
        if urlparse(original_url).scheme == '':
            original_url = 'http://' + original_url
		
        insert_row = """INSERT INTO WEB_URL (URL) VALUES ('%s')"""%(original_url)
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            try:
                result_cursor = cursor.execute(insert_row)
                encoded_string = encoding(result_cursor.lastrowid)
            except IntegrityError:
                print(original_url)
                select_row = """SELECT (ID) FROM WEB_URL WHERE URL=('%s')"""%(original_url)
                result_cursor = cursor.execute(select_row)
                encoded_string = str(result_cursor.fetchone()[0]);
        return render_template('home.html',short_url= host + encoded_string)
    return render_template('home.html')



@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded_string = decoding(short_url)
    redirect_url = 'http://localhost:5000'
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        select_row = """
                SELECT URL FROM WEB_URL
                    WHERE ID=%s
                """%(decoded_string)
        result_cursor = cursor.execute(select_row)
        try:
            redirect_url = result_cursor.fetchone()[0]
        except Exception as e:
            print (e)
    return redirect(redirect_url)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    app.run(debug=True)
