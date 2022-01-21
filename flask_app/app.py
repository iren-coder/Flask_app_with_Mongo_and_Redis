import codecs
from bson import ObjectId, json_util
import redis
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient
import json
import datetime
import gridfs

app = Flask(__name__)

r = redis.StrictRedis(host='redis', port=6379, db=0)

client = MongoClient('mongodb', 27017)
boardDB = client.newdb
db = client.boardDB
fs = gridfs.GridFS(db)


@app.route('/', methods=['GET', 'POST'])
def index():
    list_post = []

    # поиск по ID поста
    if request.method == 'POST':
        post_id = request.form['search']
        list_post.append(json.loads(r.get(post_id)))
        if len(list_post) == 0:
            return render_template('index.html', post_id=post_id)
    else:
        # Кэширование
        if r.keys():
            for key in r.keys():
                list_post.append(json.loads(r.get(key)))
        else:
            list_post = list(db.boardDB.find())

            if len(list_post) == 0:
                message = 'Здесь пока нет ни одного поста!'
                return render_template('index.html', message=message)

            json_data = json_util.dumps(list_post, ensure_ascii=True)
            list_post = json.loads(json_data)

    posts = []
    for item in list_post:
        post = {
            'id': item['_id']['$oid'],
            'title': item['title'],
            'message': item['message'],
            'author': item['author'],
            'date': item['date'],
            'tags_statistic': item['tags_statistic'],
            'comments_statistic': item['comments_statistic']
        }

        if 'image_id' in item:
            image = fs.get(ObjectId(item['image_id']['$oid']))
            base64_data = codecs.encode(image.read(), 'base64')
            image = base64_data.decode('utf-8')
            post['image'] = image

        if 'tags' in item:
            post['tags'] = ', '.join(item['tags'])

        if 'comments' in item:
            post['comments'] = item['comments']

        posts.append(post)

    return render_template('index.html', posts=posts)


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        date = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

        post = {
            'title': request.form['title'],
            'message': request.form['message'],
            'author': request.form['author'],
            'date': str(date)
        }

        if 'post_image' in request.files:
            post_image = request.files['post_image']
            post['image_id'] = fs.put(post_image, content_type="image/jpeg", filename=post_image.filename)

        if 'tag[]' in request.form:
            list_tag = request.form.getlist('tag[]')
            tags = []

            for tag in list_tag:
                if tag != '':
                    tags.append(tag)

            post['tags'] = tags
            post['tags_statistic'] = len(tags)
        else:
            post['tags_statistic'] = 0

        if 'comment[]' in request.form:
            list_com = request.form.getlist('comment[]')
            comments = []

            for comment in list_com:
                if comment != '':
                    comments.append(comment)

            post['comments'] = comments

            post['comments_statistic'] = len(comments)
        else:
            post['comments_statistic'] = 0

        # Добавление нового поста в БД
        db.boardDB.insert_one(post)

        # Добавление нового поста в кэш
        r.set(str(post['_id']), json_util.dumps(post))

        return redirect(url_for('index'))

    return render_template('add_post.html')

# Добавление нового комментария
@app.route('/leave_comment/<post_id>', methods=['GET', 'POST'])
def leave_comment(post_id):
    if request.method == 'POST':

        comment = request.form['comment']
        db.boardDB.update_many({"_id": ObjectId(post_id)}, {"$addToSet": {"comments": comment}, '$inc': {"comments_statistic": 1}})

        # Update the cache when adding a new comment
        update_post = db.boardDB.find_one({"_id": ObjectId(post_id)})
        r.set(str(post_id), json_util.dumps(update_post))

        return redirect(url_for('index'))

    return render_template('add_comment.html')

# Добавление нового тэга
@app.route('/add_tag/<post_id>', methods=['GET', 'POST'])
def add_tag(post_id):
    if request.method == 'POST':

        tag = request.form['tag']
        db.boardDB.update_many({"_id": ObjectId(post_id)}, {"$addToSet": {"tags": tag}, '$inc': {"tags_statistic": 1}})

        # Update the cache when adding a new tag
        update_post = db.boardDB.find_one({"_id": ObjectId(post_id)})
        r.set(str(post_id), json_util.dumps(update_post))

        return redirect(url_for('index'))

    return render_template('add_tag.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
