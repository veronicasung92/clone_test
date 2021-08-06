from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbsparta


## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')


## API 역할을 하는 부분

@app.route('/listing', methods=['GET'])
def listing():
    movies = list(db.netflix.find({}, {'_id' : False}).limit(10))
    return jsonify({'all_movies' : movies})

@app.route('/saving', methods=['POST'])
def saving():

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://movie.naver.com/movie/running/current.naver#', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    watch = soup.select('#content > div.article > div:nth-child(1) > div.lst_wrap > ul > li')

    for movie in watch:
        url = movie.select_one('div > a')['href']
        image = movie.select_one('div > a > img')['src']
        title = movie.select_one('dl > dt > a').text
        rating = movie.select_one('dl > dd.star > dl.info_star > dd > div > a > span.num').text[0:3]
        limit = movie.select_one('span', {'class': 'ico_rating_15'}).text
        onecat = movie.select_one('span > a:nth-child(1)', {'class': 'link_txt'}).text
        twocat = movie.select_one('span > a:nth-child(2)', {'class': 'link_txt'}).text

        doc = {
            'url': url,
            'image': image,
            'title': title,
            'rating': rating,
            'limit': limit,
            'category_1': onecat,
            'category_2': twocat,
        }

        db.netflix.insert_one(doc)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)