from flask import Flask, url_for, render_template, redirect, request, jsonify, make_response, json, flash
from flask import session as login_session
app = Flask(__name__)

import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from colorama import Fore, Style

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataSetup import Base, MenuItem, Restaurant

engine = create_engine("sqlite:///restaurantmenu.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants')
def show_restaurant():
    restaurants = session.query(Restaurant).all()
    return render_template('ShowRestaurants.html', restaurants=restaurants, login_session=login_session)


@app.route('/restaurants/add', methods=["GET", "POST"])
def add_new_restaurant():
    if 'username' not in login_session:
        return redirect('/login')
    if  request.method == "POST":
        if request.form['name']:
            newID = session.query(Restaurant).count() + 1
            name = request.form['name']
            session.add(Restaurant(id=newID, name=name))
            session.commit()
            flash('Restauran {} is added successfully.'.format(name))
        return redirect(url_for('show_restaurant'))
    elif request.method == "GET":
        return render_template("AddRestaurant.html")


@app.route('/restaurants/<int:restaurantID>/edit', methods=["POST", "GET"])
def edit_restaurant(restaurantID):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        if request.form['name']:
            name = request.form['name']
            session.query(Restaurant).filter_by(id=restaurantID).update({'name' : name})
            session.commit()
            flash('Restaurant name changed to {} successfully.'.format(name))
        return redirect(url_for('show_restaurant'))
    elif request.method == "GET":
        res = session.query(Restaurant).filter_by(id=restaurantID).one()
        return render_template('EditRestaurant.html', res=res)


@app.route('/restaurants/<int:restaurantID>/delete', methods=["GET", "POST"])
def delete_restaurant(restaurantID):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        restaurant = session.query(Restaurant).filter_by(id=restaurantID).one()
        name = restaurant.name
        session.delete(restaurant)
        session.commit()
        flash('Restaurant {} is deleted successfully.'.format(name))
        return redirect(url_for('show_restaurant'))
    elif request.method == "GET":
        res = session.query(Restaurant).filter_by(id=restaurantID).one()
        return render_template('DeleteRestaurant.html', res=res)


@app.route('/<int:restaurantID>')
@app.route('/restaurants/<int:restaurantID>')
def show_menuitem(restaurantID):
    res = session.query(Restaurant).filter_by(id=restaurantID).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurantID).all()

    return render_template('ShowMenuitem.html', menuitems=items, res=res, login_session=login_session)


@app.route('/restaurants/<int:restaurantID>/add', methods=["GET", "POST"])
def add_new_menuitem(restaurantID):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        if request.form['name']:
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            course = request.form['course']
            newID = session.query(MenuItem).count() + 1
            item = MenuItem(name=name, description=description, price=price, course=course, id=newID, restaurant_id=restaurantID)
            session.add(item)
            session.commit()
            flash('Item {} is added successfully.'.format(name))
        return redirect(url_for('show_menuitem', restaurantID=restaurantID))
    else:
        return render_template("AddMenuitem.html", resID=restaurantID)


@app.route('/restaurants/<int:restaurantID>/edit/<int:menuitemID>', methods=["GET", "POST"])
def edit_menuitem(restaurantID, menuitemID):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        if request.form['name'] and request.form['description'] and request.form['price'] and request.form['course']:
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            course = request.form['course']
            session.query(MenuItem).filter_by(id=menuitemID).update(
                {'name':name,'description':description,'price':price,'course':course})
            session.commit()
            flash('Item is edited to {} successfully.'.format(name))
        return redirect(url_for('show_menuitem', restaurantID=restaurantID))
    else:
        it = session.query(MenuItem).filter_by(id=menuitemID).one()
        return render_template("EditMenuitem.html", resID=restaurantID, it=it)


@app.route('/restaurant/<int:restaurantID>/delete/<int:menuitemID>', methods=["GET", "POST"])
def delete_menuitem(restaurantID, menuitemID):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        item = session.query(MenuItem).filter_by(id=menuitemID).one()
        name = item.name
        session.delete(item)
        session.commit()
        flash('Item {} is deleted successfully.'.format(name))
        return redirect(url_for('show_menuitem', restaurantID=restaurantID))
    else:
        it = session.query(MenuItem).filter_by(id=menuitemID).one()
        return render_template("DeleteMenuitem.html", resID=restaurantID, it=it)


@app.route('/restaurants/JSON')
def get_restaurants():
    restaurants = session.query(Restaurant).all()
    return jsonify([res.serialize for res in restaurants])


@app.route('/restaurants/<int:restaurantID>/menu/JSON')
def get_items(restaurantID):
    items = session.query(MenuItem).filter_by(id=restaurantID).all()
    return jsonify([res.serialize for res in items])


@app.route('/restaurants/<int:restaurantID>/menu/<int:menuitemID>/JSON')
def get_item(restaurantID, menuitemID):
    item = session.query(MenuItem).filter_by(id=menuitemID).one()
    return jsonify(item.serialize)


@app.route("/login")
def user_login():
    state = ''.join((random.choice(string.ascii_uppercase + string.digits) for _ in range(32)))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route("/gconnect", methods=['POST'])
def gconnect():
    print("{}gconnect starts{}".format(Fore.GREEN,Style.RESET_ALL))
    if request.args.get('state') != login_session['state']:
        print("{}Exchange Code is Wrong{}".format(Fore.BLUE, Style.RESET_ALL))
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')  # Mistake is happening here
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        print("{}Flow Exchange Error is Raised{}".format(Fore.BLUE, Style.RESET_ALL))
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode("ascii"))
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and stored_credentials == stored_gplus_id:
        response = make_response(json.dumps("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'

    # login_session['credentials'] = credentials
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
        # It reaches this point, there is only a little to do guy
    print(login_session['username'])
    output = '<body>'
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '</h1>'
    output += '<body>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print("done!")
    flash('{} login is successful'.format(login_session['username']))
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        flash('{} logout is successful'.format(login_session['username']))
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successflly disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/restaurants')
    else:
        response = make_response(json.dumps('Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response





if __name__ == "__main__":
    app.debug = True
    app.secret_key="useless keyword"
    app.run(host="0.0.0.0", port=5000)