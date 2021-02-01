from flask_table import Table, Column

class Results(Table):
    id = Column('id', show=False)
    title = Column('title')
    author = Column('author')
    date_published = Column('date published')