import ConfigParser, sys, os, pymongo, bcrypt
from babel import dates
from datetime import date, datetime
from flask import Flask, url_for, render_template, request, redirect, session
from flask_babel import Babel, gettext
from bson.objectid import ObjectId
from static.pythonscript.AESencryption import encrypt, decrypt
app = Flask(__name__)
babel = Babel(app)
AES_key = "1ZK91d+7pMe+U3m+DdNnUA=="
dbClient = pymongo.MongoClient("mongodb://<admin>:<X7R9gxnwzUkQ5ZR>@ds063909.mlab.com:63909/webshopapp-napier")
app.secret_key = "K*GH^$DB$%:DLC@SHCT2S735SNC*&hd5"
app.config["BABEL_DEFAULT_LOCALE"] = "en"

# Database
dbConnection = pymongo.MongoClient("ds063909.mlab.com", 63909)
db = dbConnection["webshopapp-napier"]
db.authenticate("admin", "X7R9gxnwzUkQ5ZR")
dbUsers = db["users"]
dbOrders = db["orders"]

def init(app, configFile):
    # App initialization, reading from config file #
    # Config file name must be passed in by argument #
    config = ConfigParser.ConfigParser()
    try:
        config_location = "etc/Configs/" + configFile + ".cfg"
        config.read(config_location)

        # get config values
        app.config['IP_ADDRESS'] = config.get("config", "IP_ADDRESS")

        if configFile == "heroku": # if on Heroku - read and assign the DYNAMIC PORT
            app.config['PORT'] = os.environ.get("PORT", 33507)
        else:   # if not on Heroku - read PORT FROM CONFIG FILE
            app.config['DEBUG'] = config.get("config", "DEBUG")
            app.config['PORT'] = config.get("config", "PORT")

        print " * File read from config file OK! (" + config_location + ")"
    except:
        print " *** File read from config file FAILED! (" + config_location + ")"

@app.route("/language/<lang>/<pathname>")
def language_change(lang, pathname):
    session["lang"] = lang

    if pathname == "root":
        return redirect("/")
    return redirect("/" + pathname)
@babel.localeselector
def select_locale():
    try: # if cookie exists
        return session["lang"];
    except: # return default locale
        return "en";
def getBagListCount():
    if "bag" in session:
        return len(session["bag"])
    else:
        return 0
def getUser():
    if "user" in session:
        return session["user"]
    else:
        return None
def getUserBag():
    if "user" in session:
        return dbUsers.find_one({"email":session["user"]["email"]})["bag"]
    else:
        return None
def updateDBUserBag():
    if getUser() != None: # User is logged in, store items in database
        userID = dbUsers.find_one({"email": getUser()["email"]})["_id"]
        if "bag" not in session:
            dbUsers.update_one({'_id':userID}, {"$set": {"bag":None}}, upsert=False)
        else:
            dbUsers.update_one({'_id':userID}, {"$set": {"bag":session["bag"]}}, upsert=False)

@app.route("/")
def index():
    return render_template('index.html', title=gettext("Home"), bagListCount=getBagListCount(), user=getUser(),
     carousel23RowRange=range(6), carousel1Range=range(9), carousel23Range=range(4), carousel4Range=range(5), carousel5Range=range(7), carousel6Range=range(7))

filters = [gettext("Round"), gettext("Heart"), gettext("Coming soon"), gettext("Coming soon"), gettext("Coming soon"), gettext("Customise")]
@app.route("/products")
def products():
    numberofproducts = 138
    return render_template('products.html', title=gettext("Products"), bagListCount=getBagListCount(), user=getUser(), selected=None, Filters= filters, productIDs=range(1, numberofproducts))
@app.route("/products/round")
def products_round():
    numberofproducts = 100
    return render_template('products.html', title=gettext("Products"), bagListCount=getBagListCount(), user=getUser(), selected="Round", Filters= filters, productIDs=range(1, numberofproducts))
@app.route("/products/heart")
def products_heart():
    numberofproducts = 37
    return render_template('products.html', title=gettext("Products"), bagListCount=getBagListCount(), user=getUser(), selected="Heart", Filters= filters,  productIDs=range(101, 101 + numberofproducts))
@app.route("/products/customise")
def products_customise():
    return render_template('customise.html', title=gettext("Products"), bagListCount=getBagListCount(), user=getUser(), selected="Customise", Filters= filters)

@app.route("/products/addtobag/<id>/<amount>")
def products_add(id, amount):
    inBag = False
    if "bag" not in session: # bag is empty
        bagList = []
        bagList.append([id, amount])
        session["bag"] = bagList
    else:
        bagList = session["bag"]
        for item in bagList:
            if item[0] == id: # if the item is in the bag already, update the count, return to bag
                inBag = True
                item[1] = amount
                session["bag"] = bagList
                updateDBUserBag()
                return redirect("/bag")
        bagList.append([id, amount]) # add item to bag
        session["bag"] = bagList

    updateDBUserBag()

    return redirect("/products")

@app.route("/products/removefrombag/<id>/<amount>")
def products_remove(id, amount):
    bagList = session["bag"]
    try:
        bagList.remove([id, amount])
        session["bag"] = bagList
        if len(bagList) == 0:
            session.pop("bag")
    except:
        print "Could not remove item(" + id + ")"

    updateDBUserBag()

    return redirect("/bag")

@app.route("/events")
def events():
    eventDates = [None] * 2
    eventDates[0] = [ date(2018, 12, 22), date(2018, 12, 24) ] # date N, from - to
    eventDates[1] = [ date(2019, 12, 22), date(2019, 12, 24) ]
    # ENG
    eng_eventDates = [None] * len(eventDates)
    i = 0;
    for event in eventDates:
        eng_eventDates[i] = [ dates.format_date(event[0], format='long', locale='en_UK'), dates.format_date(event[1], format='long', locale='en_UK') ]
        i = i + 1;
    # HUN
    hun_eventDates = [None] * len(eventDates)
    i = 0;
    for event in eventDates:
        hun_eventDates[i] = [ dates.format_date(event[0], format='long', locale='hu_HU'), dates.format_date(event[1], format='long', locale='hu_HU') ]
        i = i + 1;

    try:
        if session["lang"] == "hu":
            return render_template('events.html', title=gettext("Events"), bagListCount=getBagListCount(), user=getUser(), carousel1Range=range(6), eventDates=hun_eventDates)
    except: return render_template('events.html', title=gettext("Events"), bagListCount=getBagListCount(), user=getUser(), carousel1Range=range(6), eventDates=eng_eventDates)
    return render_template('events.html', title=gettext("Events"), bagListCount=getBagListCount(), user=getUser(), carousel1Range=range(6), eventDates=eng_eventDates)

@app.route("/about")
def about():
    return render_template('about.html', title=gettext("About"), bagListCount=getBagListCount(), user=getUser())

@app.route("/orders")
def orders():
    if getUser() != None and decrypt(AES_key, getUser()["email"]) == "admin@admin":
        orders = []
        for order in dbOrders.find():
            orders.append(order)

        return render_template('orders.html', title=gettext("Orders"), bagListCount=getBagListCount(), user=getUser(), orders=orders)
    return redirect("/")
@app.route("/orders/completed/<orderID>")
def orderCompleted(orderID):
    orderID = ObjectId(orderID)
    if "completed" in dbOrders.find_one({"_id":orderID}) and dbOrders.find_one({"_id":orderID})["completed"] == True:
        dbOrders.update_one({"_id":orderID}, {"$set": {"completed":False}}, upsert=False)
    else:
        dbOrders.update_one({"_id":orderID}, {"$set": {"completed":True}}, upsert=False)

    return redirect("/orders")
@app.route("/orders/important/<orderID>")
def orderImportant(orderID):
    orderID = ObjectId(orderID)
    if "important" in dbOrders.find_one({"_id":orderID}) and dbOrders.find_one({"_id":orderID})["important"] == True:
        dbOrders.update_one({"_id":orderID}, {"$set": {"important":False}}, upsert=False)
    else:
        dbOrders.update_one({'_id':orderID}, {"$set": {"important":True}}, upsert=False)

    return redirect("/orders")
@app.route("/orders/delete/<orderID>")
def orderDelete(orderID):
    orderID = ObjectId(orderID)
    dbOrders.remove({"_id":orderID})

    return redirect("/orders")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/logout")
    if "registeredEmail" in session:
        registeredEmail = session["registeredEmail"]
    else:
        registeredEmail = None
    error = None

    if request.method == "POST":
        email = encrypt(AES_key, request.form["email"])
        password = request.form["password"]
        rememberpw = False
        if "rememberpw" in request.form:
            rememberpw = True

        for user in dbUsers.find():
            if user["email"] == email and bcrypt.checkpw(password.encode('utf-8'), user["pw"].encode('utf-8')):
                if rememberpw:#TODO AUTOFILL
                    session["user"] = {"email": email, "pw": bcrypt.hashpw(password.encode('utf-8'), user["pw"].encode('utf-8'))}
                else:
                    session["user"] = {"email": email}
                # Get items from DB
                dbUserBag = dbUsers.find_one({"email":email})["bag"]
                if dbUserBag != None:
                    session["bag"] = dbUsers.find_one({"email":email})["bag"]

                return redirect("/")

        error = gettext("Incorrect email/password combination")
        return render_template('login.html', title=gettext("Login"), bagListCount=getBagListCount(), user=getUser(), registeredEmail=registeredEmail, error=error)

    return render_template('login.html', title=gettext("Login"), bagListCount=getBagListCount(), user=getUser(), registeredEmail=registeredEmail, error=error)

@app.route("/logout")
def logout():
    session.pop("user")
    if "bag" in session:
        session.pop("bag")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = encrypt(AES_key, request.form["email"])
        password = bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt())

        for user in dbUsers.find():
            if user["email"] == email: # account already registered
                error = gettext("Account already exists!")
                return render_template('register.html', title=gettext("Register"), bagListCount=getBagListCount(), user=getUser(), error=error)
        # If account is not registered, register
        if "bag" in session:
            dbUsers.insert_one({"email":email, "pw":password, "bag":session["bag"]})
        else:
            dbUsers.insert_one({"email":email, "pw":password, "bag":[]})
        session["registeredEmail"] = decrypt(AES_key, email)
        return redirect("/login")

    return render_template('register.html', title=gettext("Register"), bagListCount=getBagListCount(), user=getUser(), error=None)

@app.route("/bag")
def bag():
    bagList = []
    if "bag" in session:
        bagList = session["bag"]
        bagListCount = getBagListCount()

        lang = "en"
        BASEPRICE = 1.29 # english baseprice
        if "lang" in session:
            lang = session["lang"]
            if lang == "hu":
                BASEPRICE = 399 # hungarian baseprice

        price = 0.0;
        for item in bagList:
            price = price + float(item[1]) * BASEPRICE

        return render_template('bag.html', title=gettext("Bag"), bagListCount=getBagListCount(), user=getUser(), price=price, lang=lang, bagList=bagList)
    else:
        bagList = None
        return render_template('bag.html', title=gettext("Bag"), bagListCount=getBagListCount(), user=getUser(), bagList=bagList)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if getUser() == None:
        return redirect("/login")
    if request.method == "POST": # incoming order
        name = request.form["name"]
        address = request.form["address"]
        city = request.form["city"]
        country = request.form["country"]
        postcode = request.form["postcode"]
        order = session["bag"]
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Insert order to DB
        dbOrders.insert_one({"name":name, "address":address, "city":city, "country":country, "postcode":postcode, "date":date, "bag":order})

        session.pop("bag")
        return redirect("/")
    else:
        if "user" not in session:
            return redirect("/login")

        bagList = []
        if "bag" in session:
            bagList = session["bag"]
            bagListCount = getBagListCount()

            lang = "en"
            BASEPRICE = 1.29 # english baseprice
            if "lang" in session:
                lang = session["lang"]
                if lang == "hu":
                    BASEPRICE = 399 # hungarian baseprice

            price = 0.0;
            for item in bagList:
                price = price + float(item[1]) * BASEPRICE

    return render_template('checkout.html', title=gettext("Checkout"), bagListCount=getBagListCount(), user=getUser(), price=price, lang=lang)



if __name__ == '__main__':
    try:  # load config file
        init(app, sys.argv[1])
        app.run( # run app
            host = app.config['IP_ADDRESS'],
            port = int(app.config['PORT'])
        )
    except:
        app.run( # run app
            host = "0.0.0.0",
            debug = True,
            port = 5000
        )
