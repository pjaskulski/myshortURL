from myshorturl import db, Link
import os
from urllib.parse import unquote


basedir = os.path.abspath(os.path.dirname(__file__))
if not os.path.exists(os.path.join(basedir, 'links.db')):
    db.create_all()
    idlink = 'qwertyuiop'
    adres = 'https%3A%2F%2Fflask-sqlalchemy.palletsprojects.com%2Fen%2F2.x%2Fquickstart%2F%23a-minimal-application'
    my_link = Link(idlink, unquote(adres))
    db.session.add(my_link)
    db.session.commit()
