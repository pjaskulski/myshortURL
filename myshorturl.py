# aplikacja myshortURL
from flask import Flask, redirect, request, render_template, make_response, jsonify, escape
from flask_sqlalchemy import SQLAlchemy
import os
from random import randrange
from urllib.parse import unquote


app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'links.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Link(db.Model):
    """ Link table """
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True)
    idlink = db.Column(db.String(10), unique=True, nullable=False)
    adres = db.Column(db.String(255), unique=False, nullable=False)
    title = db.Column(db.String(255), unique=False, nullable=True)

    def __init__(self, idlink, adres, title=""):
        self.idlink = idlink
        self.adres = adres
        self.title = title

    def __repr__(self):
        return "<Link({}, {}, {})>".format(self.idlink, self.adres, self.title)


def random_short(lenght=10):
    """ 
    Metoda generuje losowy ciąg znaków o zadanie długości, 
    który będzie wykorzystany jako identyfikator skrótu 
    """
    lista = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
             't', 'u', 'w', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    max = len(lista)
    result = ''
    for i in range(1, lenght + 1):
        result += lista[randrange(0, max)]

    return result


def verify_short(t_short):
    """ 
    Weryfikacja czy podany skrót jest nowym nieistniejącym w bazie skrótrem 
    """
    test_link = Link.query.filter_by(idlink=t_short).first()
    if test_link != None:
        return False
    else:
        return True


def create_short():
    """
    Metoda tworzy nowy skrót
    """
    short = ""
    while True:
        short = random_short()
        if verify_short(short):
            break

    return short


@app.route('/')
def hello_world():
    return 'Serwis myshortURL'


@app.route('/api/create-link')
def api_create_link():
    headers = {"Content-Type": "application/json"}
    if 'url' in request.args:
        adres = request.args['url']
        my_adres = unquote(adres)
        if not my_adres.startswith('http'):
            my_adres = 'http://' + my_adres
        idlink = create_short()
        my_link = Link(idlink, my_adres)
        db.session.add(my_link)
        db.session.commit()
        my_dict = {idlink: my_adres}
        return make_response(jsonify(my_dict), 200, headers)
    else:
        my_dict = {'ERROR': 'No url parameter'}
        return make_response(jsonify(my_dict), 200, headers)


@app.route('/<idlink>')
def link(idlink):
    test_link = Link.query.filter_by(idlink=idlink).first()
    if test_link != None:
        return redirect(test_link.adres)
    else:
        #user_agent = request.headers.get('User-Agent')
        return "Przekazano nieznany link: {}".format(idlink)


if __name__ == '__main__':
    app.run(debug=True)
