import os
import random

import flask
from flask import Flask, render_template, url_for, request, session, redirect
import sqlite3
import hashlib

app = Flask(__name__)

app.config['SECRET_KEY'] = '6323422092:AAGtEOJWhvjfW411obuNeIM1T_e0NP3dsNM'



menu = [
    {"name": "главная", "url": "/"},
    {"name": "авто", "url": "avto"},
    {"name": "рег", "url": "reg"}
]








@app.route("/insert", methods=['POST'])
def insert():

    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    hashas = hashlib.md5(request.form["pass"].encode())
    passw = hashas.hexdigest()
    cursor.execute('''INSERT INTO users('login', password) VALUES(?, ?)''', (request.form["log"],passw))
    connect.commit()

    user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()

    session['user_login'] =user[1]
    menu = [
        {"name": "главная", "url": "/"},
        {"name": session['user_login'], "url": "profile"},

    ]


    hrefs = cursor.execute(
        '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
        (session['user_id'],)).fetchall()
    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

    return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)





@app.route("/check", methods=['POST'])
def check():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()

    user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()
    hashas = hashlib.md5(request.form["pass"].encode())
    passw = hashas.hexdigest()
    menu = [
        {"name": "главная", "url": "/"},
        {"name": "авто", "url": "avto"},
        {"name": "рег", "url": "reg"}
    ]
    if user!=None:
        if passw==user[2]:

            session['user_login'] = user[1]
            session['user_id'] = user[0]
            hrefs = cursor.execute('''SELECT * FROM 'links' WHERE user_id = ?''', (session['user_id'],)).fetchall()
            menu = [
                {"name": "главная", "url": "/"},
                {"name": session['user_login'], "url": "profile"},
            ]
            if 'adres' in session and session['adres']!=None:
                if session['type']==2:
                    ad = session['adres']
                    session['adid'] = None
                    session['type'] = None
                    session['adres']=None
                    return redirect(f"{ad}")
                else:
                    if session['adid']==session['user_id']:
                        ad = session['adres']
                        session['adid'] = None
                        session['type'] = None
                        session['adres'] = None
                        return redirect(f"{ad}")
                    else:
                        return 'ссылка приват и не ваша'
            else:
                hrefs = cursor.execute(
                    '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                    (session['user_id'],)).fetchall()
                type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

                return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)
        else:

            flask.flash('пароль не подходит')
            return render_template('avto.html', title="Авто", menu=menu)
    else:

        flask.flash('такого акка нет')
        return render_template('avto.html', title="Авто", menu=menu)



@app.route("/delete", methods=['POST'])
def delete():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    cursor.execute('''DELETE FROM 'links' WHERE id = ?''', (request.form['idd'],))
    hrefs = cursor.execute(
        '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
        (session['user_id'],)).fetchall()
    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

    return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)





@app.route("/short", methods=['POST'])
def short():
    if 'user_login' in session and session['user_login'] !=None:
        menu = [
            {"name": "главная", "url": "/"},
            {"name": session['user_login'], "url": "profile"},

        ]
    else:
        menu = [
            {"name": "главная", "url": "/"},
            {"name": "авто", "url": "avto"},
            {"name": "рег", "url": "reg"}
        ]
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    if request.form['how']=='1':

        if ('user_id' in session and session['user_id']!=None):
            user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]

            cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id') VALUES(?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how']))
            connect.commit()
            return f'/href/{user_adress}'
        else:
            user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
            cursor.execute('''INSERT INTO links('link', 'hreflink', 'link_type_id') VALUES(?, ?, ?)''', (request.form['href'], user_adress, request.form['how']))
            connect.commit()
            flask.flash(f'{user_adress}')
            return render_template('index.html', title="Главная", menu=menu)



    elif request.form['how']=='2':
        user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
        cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id') VALUES(?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how']))
        connect.commit()
        flask.flash(f'{user_adress}')
        return render_template('index.html', title="Главная", menu=menu)
    else:
        user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
        cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id') VALUES(?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how']))
        connect.commit()
        flask.flash(f'{user_adress}')
        return render_template('index.html', title="Главная", menu=menu)


@app.route("/href/<hashref>")
def direct(hashref):
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    href = cursor.execute('''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''', (hashref, ) ).fetchone()

    if href[4]==1:
        return redirect(f"{href[1]}")

    elif href[4]==2:
        if 'user_id' in session and session['user_id']!=None:
            return redirect(f"{href[1]}")

        else:
            session['adres'] = href[1]
            session['type'] = 2
            session['adid'] = href[3]
            menu = [
                {"name": "главная", "url": "/"},
                {"name": "авто", "url": "/avto"},
                {"name": "рег", "url": "/reg"}
            ]
            return render_template('avto.html', title="Главная", menu=menu)

    elif href[4]==3:
        if 'user_id' in session and session['user_id'] != None:
            if (href[3]==session['user_id']):
                return redirect(f"{href[1]}")
            else:
                return 'ссылка приватная и не ваша так что соре'
        else:
            session['adres'] = href[1]
            session['type'] = 3
            session['adid'] = href[3]
            menu = [
                {"name": "главная", "url": "/"},
                {"name": "авто", "url": "/avto"},
                {"name": "рег", "url": "/reg"}
            ]
            return render_template('avto.html', title="Главная", menu=menu)





@app.route("/logout", methods=['POST'])
def logout():
    session['user_login']=None
    session['user_id'] = None
    return render_template('index.html', title="Главная", menu=menu)




@app.route("/updatehref", methods=['POST'])
def updatehref():

    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    name = cursor.execute('''SELECT * FROM 'links' WHERE hreflink = ? ''', (request.form["hreflink"],)).fetchone()

    menu = [
        {"name": "главная", "url": "/"},
        {"name": session['user_login'], "url": "profile"},

    ]

    if (name !=None):
        if (name[3]==session['user_id']):
            if (request.form["types"]!='0'):
                cursor.execute('''UPDATE links SET link_type_id = ? WHERE id = ?''', (request.form["types"],request.form["idlink"]))
                connect.commit()
                flask.flash('все успешно изменено')
                hrefs = cursor.execute('''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',(session['user_id'],)).fetchall()
                type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

                return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)
            else:
                flask.flash('зач')
                hrefs = cursor.execute('''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',(session['user_id'],)).fetchall()
                type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
                return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)
        else:
            flask.flash(f'имя {request.form["hreflink"]} уже занято')
            hrefs = cursor.execute(
                '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                (session['user_id'],)).fetchall()
            type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
            return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)

    else:
        if (request.form["types"]!='0'):
            cursor.execute('''UPDATE links SET hreflink = ?, link_type_id = ? WHERE id = ?''',(request.form["hreflink"], request.form["types"], request.form["idlink"]))
            connect.commit()
            flask.flash('все успешно изменено')
            hrefs = cursor.execute(
                '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                (session['user_id'],)).fetchall()
            type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
            return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)
        else:
            cursor.execute('''UPDATE links SET hreflink = ? WHERE id = ?''',(request.form["hreflink"], request.form["idlink"]))
            connect.commit()
            flask.flash('все успешно изменено')
            hrefs = cursor.execute(
                '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                (session['user_id'],)).fetchall()
            type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
            return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)

    # UPDATE links SET hreflink = ?, link_type_id = ? WHERE id = ?







@app.route("/")
def index():
    if 'user_login' in session and session['user_login'] !=None:
        menu = [
            {"name": "главная", "url": "/"},
            {"name": session['user_login'], "url": "profile"},

        ]
    else:
        menu = [
            {"name": "главная", "url": "/"},
            {"name": "авто", "url": "avto"},
            {"name": "рег", "url": "reg"}
        ]
    return render_template('index.html', title="Главная", menu=menu)



@app.route("/reg")
def reg():
    return render_template('reg.html', title="Рег", menu=menu)


@app.route("/avto")
def avto():
    return render_template('avto.html', title="Авто", menu=menu)

@app.route("/profile")
def profile():
    if 'user_login' in session and session['user_login']!=None:
        menu = [
            {"name": "главная", "url": "/"},
            {"name": session['user_login'], "url": "profile"},

        ]
    else:
        menu = [
            {"name": "главная", "url": "/"},
            {"name": "авто", "url": "avto"},
            {"name": "рег", "url": "reg"}
        ]
        return render_template('index.html', title="Главная", menu=menu)

    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()

    hrefs = cursor.execute('''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',(session['user_id'],)).fetchall()
    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

    return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)


if __name__ =="__main__":
    app.run(debug=True)