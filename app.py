from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from datetime import datetime


app = Flask(__name__)
api = Api(app)
app.secret_key = 'monkey'
images = Images(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    genre = db.Column(db.String(30), nullable=False)
    book_rating = db.Column(db.Integer, nullable=False, default = 'N/A')
    publisher = db.Column(db.String(30), nullable=False, default = 'N/A')
    comments = db.Column(db.String(30), nullable=False, default = 'N/A')
    date_published = db.Column(db.DateTime, nullable=False)





@app.route('/book/<int:id>')
def bookpage(id):
    post = Book.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/home')

@app.route('/results')
def search_results(search):
    results = []
    search_keyword = search.data['search']

    if search_keyword:
        if search.data['select'] == 'author':
            qry = db_session.query(Book).filter(Book.author.contains(search_keyword))
            results = [item[0] for item in qry.all()]
        elif search.data['select'] == 'title':
            qry = db_session.query(Book).filter(Book.title.contains(search_keyword))
            results = qry.all()
        elif search.data['select'] == 'genre':
            qry = db_session.query(Book).filter(Book.genre.contains(search_keyword))
            results = qry.all()
        elif search.data['select'] == 'publisher':
            qry = db_session.query(Book).filter(Book.publisher.contains(search_keyword))
            results = qry.all()
    else:
        qry = db_session.query(Book)
        results = qry.all()

    else:
        qry = db_session.query(Book)
        results = qry.all()
        if not results:
        flash('No results found!')
        return redirect('/')
        else:
        table =Results(results)
        table.border = True
        return render_template('results.html', table=table)
            


if __name__ = '__main__':
    app.run(debug=True)
