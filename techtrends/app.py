import sqlite3

from flask import Flask, json, render_template, request, url_for, redirect, flash
from logging import basicConfig, DEBUG, StreamHandler
from sys import stderr, stdout

db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    db_connection_count += 1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute(
        'SELECT * FROM posts WHERE id = ?',
        (post_id,)
    ).fetchone()
    connection.close()
    app.logger.info("Article has been requested.")
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error("Article {} could not be found".format(post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info("Article {} has been accessed".format(post_id))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About page has been requested")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute(
                'INSERT INTO posts (title, content) VALUES (?, ?)',
                (title, content)
            )
            connection.commit()
            connection.close()
            app.logger.info("A new article has been created.")
            return redirect(url_for('index'))
    return render_template('create.html')

# Health Check
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
        mimetype='application/json',
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
    )
    app.logger.info('Status request successfull')
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    response = app.response_class(
        mimetype='application/json',
        response=json.dumps({
            "status": "success",
            "code": 0,
            "data": {"db_connection_count": db_connection_count, "post_count": post_count}
        }),
        status=200,
    )
    app.logger.info('Metrics request successfull')
    return response

# start the application on port 3111
if __name__ == "__main__":  
    basicConfig(
        format='%(levelname)s: %(name)-2s - [%(asctime)s] - %(message)s',
        handlers=[StreamHandler(stdout), StreamHandler(stderr)],
        level=DEBUG,
    )
    app.run(host='0.0.0.0', port='3111')
