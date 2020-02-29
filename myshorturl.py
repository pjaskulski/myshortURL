# app myshortURL
from flask import Flask, redirect, request, render_template, make_response, jsonify, escape, abort
from flask import url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
import os
from random import randrange
from urllib.parse import unquote
from datetime import datetime


app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'links.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'this jacket is blue'
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)


class Link(db.Model):
    """Link table definition"""
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True)
    idlink = db.Column(db.String(10), unique=True, nullable=False)
    adres = db.Column(db.String(255), unique=False, nullable=False)
    title = db.Column(db.String(255), unique=False, nullable=True)
    users_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), unique=False, nullable=True)
    statlink = db.relationship('StatLink', backref='statlink')

    def __init__(self, idlink, adres, title="", users_id=None):
        self.idlink = idlink
        self.adres = adres
        self.title = title
        self.users_id = None

    def __repr__(self):
        return "<Link({}, {}, {})>".format(self.idlink, self.adres, self.title)


class Users(db.Model):
    """Users table definition"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=False, nullable=False)
    link = db.relationship('Link', backref='user')

    def __init__(self, name, password, email):
        self.name = name
        self.passoword = password
        self.email = email

    def __repr__(self):
        return "<User({}, {})>".format(self.name, self.email)


class StatLink(db.Model):
    """StatLink table definition"""
    __tablename__ = "statlink"

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'))
    date = db.Column(db.DateTime)
    remote_ip = db.Column(db.String(25), unique=False, nullable=True)

    def __init__(self, link_id, date, remote_ip):
        self.link_id = link_id
        self.date = date
        self.remote_ip = remote_ip

    def __repr__(self):
        return "<StatLink({}, {}, {})>".format(self.link_id, self.date, self.clientip)


class IndexForm(FlaskForm):
    """Form for entering a URL"""
    adres = StringField('URL Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


def random_short(lenght=10):
    """The method generates a random string of characters of a given length, 
    which will be used as a shortcut identifier 
    """
    lista = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
             't', 'u', 'w', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    max = len(lista)
    result = ''
    for i in range(1, lenght + 1):
        result += lista[randrange(0, max)]

    return result


def verify_short(t_short):
    """Verification whether the short-link given is a new one that does not exist in the database
    """
    test_link = Link.query.filter_by(idlink=t_short).first()
    if test_link != None:
        return False
    else:
        return True


def create_short():
    """method generates a new short-link
    """
    short = ""
    while True:
        short = random_short()
        if verify_short(short):
            break

    return short


def short_from_adres(adres):
    """create short-link from url

    parameter: 
        adres - url
    """
    my_adres = unquote(adres)
    if not my_adres.startswith('http'):
        my_adres = 'http://' + my_adres
    idlink = create_short()
    my_link = Link(idlink, my_adres)
    db.session.add(my_link)
    db.session.commit()
    return idlink


@app.route('/', methods=['GET', 'POST'])
def index():
    """index - website homepage, form for creating a shor-link 
    """
    form = IndexForm()
    myserver = request.host_url
    if form.validate_on_submit():
        adres = form.adres.data
        if 'adres' not in session or session['adres'] != adres:
            new_link = short_from_adres(adres)
            session['adres'] = adres
            session['link'] = new_link
            return render_template('link.html', adres=form.adres.data, new_link=myserver+new_link)
        else:
            return render_template('link.html', adres=session.get('adres'), new_link=myserver+session.get('link'))

    return render_template('index.html', form=form)


@app.route('/about')
def about():
    """Displays page about the service
    """
    return render_template('about.html')


@app.route('/api/create-link')
def api_create_link():
    """Create new short-link by api
    """
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
    """
    redirect from short-link to destination
    """
    test_link = Link.query.filter_by(idlink=idlink).first()
    if test_link != None:
        remote_ip = request.remote_addr
        stat_link = StatLink(test_link.id, datetime.now(), remote_ip)
        db.session.add(stat_link)
        db.session.commit()

        return redirect(test_link.adres)
    else:
        myserver = request.host_url
        return render_template('unknown.html', idlink=myserver+idlink)


if __name__ == '__main__':
    app.run(debug=True)
