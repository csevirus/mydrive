from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
import os
import bitly_api
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('myfiles', __name__)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = "/home/csevirus/project/mydrive/uploads"
DOMAIN_NAME = "http://127.0.0.1:5000"
BITLY_ACCESS_TOKEN ="c09aa3f62d052e9c97e87923b412b2410dd865c7"

@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, description, created, author_id, username, extension'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.author_id = ?',
        (g.user['id'],)
    ).fetchall()
    return render_template('myfiles/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        file = request.files['file']
        db = get_db()
        error = None
        if not title or '.' in title:
            error = 'Title is empty or invalid.'
        if file.filename == '':
            error = 'No selected file'
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = title + '.' + extension
        if file and extension in ALLOWED_EXTENSIONS:
            filename = secure_filename(filename)
        else:
            error = 'file extention not permited by the server'
        if db.execute(
            'SELECT title FROM post WHERE title = ?', (title,)
        ).fetchone() is not None:
            error = 'Title {} is already used.'.format(title)
        if error is not None:
            flash(error)
        else:
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            db.execute(
                'INSERT INTO post (title, description, author_id, extension)'
                ' VALUES (?, ?, ?, ?)',
                (title, description, g.user['id'], extension)
            )
            db.commit()
            return redirect(url_for('myfiles.index'))
    return render_template('myfiles/create.html')

def get_post(id):
    post = get_db().execute(
        'SELECT p.id, title, description, created, author_id, username, extension'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if post['author_id'] != g.user['id']:
        abort(403)
    return post

@bp.route('/<int:id>/getfile', methods=('GET', 'POST'))
@login_required
def getfile(id):
    post = get_post(id)
    filename = post['title'] + '.' + post['extension']
    return uploaded_file(filename)

@bp.route('/<filename>/uploads')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@bp.route('/<int:id>/share')
def share(id):
    post = get_post(id)
    b = bitly_api.Connection(access_token = BITLY_ACCESS_TOKEN)
    filename = post['title']+'.'+post['extension']
    link = DOMAIN_NAME + url_for('myfiles.uploaded_file',filename = filename)
    link = b.shorten(link)
    flash("LINK : " + link['url'])
    return redirect(url_for('myfiles.index'))

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None
        db = get_db()
        if not title:
            error = 'Title is required.'
        if db.execute(
            'SELECT title FROM post WHERE title = ? and id != ?', (title,id)
        ).fetchone() is not None:
            error = 'Title {} is already used.'.format(title)
        oldfilename = post['title'] + '.' + post['extension']
        newfilename = title + '.' + post['extension']
        newfilename = secure_filename(newfilename)
        if error is not None:
            flash(error)
        else:
            os.rename(os.path.join(UPLOAD_FOLDER, oldfilename ),os.path.join(UPLOAD_FOLDER, newfilename ))
            db.execute(
                'UPDATE post SET title = ?, description = ?'
                ' WHERE id = ?',
                (title, description, id)
            )
            db.commit()
            return redirect(url_for('myfiles.index'))
    return render_template('myfiles/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST','GET'))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('myfiles.index'))
