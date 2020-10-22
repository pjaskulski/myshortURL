from myshorturl import db
import os
from urllib.parse import unquote


basedir = os.path.abspath(os.path.dirname(__file__))
if not os.path.exists(os.path.join(basedir,'db', 'links.sqlite')):
    db.create_all()
    db.session.commit()
