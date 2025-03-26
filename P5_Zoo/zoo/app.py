from flask import Flask, render_template, request, redirect, session, abort, flash
from flask_session import Session
from datetime import datetime
import queries as q # tells app.py about the queries.py file


app = Flask(__name__)
app.config["SESSION_TYPE"] = "cachelib"
app.config["SESSION_PERMANENT"] = False
Session(app)
app.secret_key = "thisisnotsecret"



@app.route("/")
def index():
    # get the names of all the exhibits
    exhibits = q.get_exhibit_names()
    return render_template("index.html", exhibits=exhibits)

@app.post("/exhibits")
def exhibits():
    # get the exhibit name from the form
    name = request.form.get("exhibit-name")
    session["exhibit"] = name
    flash(f"We will remember {name}")
    # ask the database for the details
    details = q.get_exhibit_details(name)
    if not details:
        abort(404)
    else:
        return render_template("exhibit_detail.html", exhibit=details)

@app.route("/animals/<exhibit>")
def animals(exhibit):
    animals_list = q.get_animals_by_exhibit(exhibit)

    return render_template("animals.html", animals=animals_list)

@app.route("/animals")
def show_animals():
    if session.get("exhibit"): # is there an exhibit in the session?
        return redirect(f"/animals/{session.get('exhibit')}")
    else: # no session exhibit
        return redirect("/")

@app.route("/animals/<int:animal_id>")
def animal_details(animal_id):
    # get the animal details
    animal_details = q.get_animal_details(animal_id)
    if animal_details:
        # create a html template page that shows off the details of the
        # selected animal
        return render_template("animal_details.html", animal=animal_details)
    else:
        abort(404)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # process the form
        animal = {
            "species": request.form.get("species"),
            "diet": request.form.get("diet"),
            "description": request.form.get("description"),
            "population": int(request.form.get("population")),
            "habitat": request.form.get("habitat"),
            "exhibit": request.form.get("exhibit")
        }
        # now add the animal to our database
        animal_id = q.add_animal(animal)
        if animal_id > 0:
            flash(f"Success! The {animal.get('species')} was added to the database.")
        return redirect(f"/animals/{animal_id}")
    else:  # show the form
        # get the exhibits
        exhibits = q.get_exhibit_names()
        return render_template("add.html", exhibits=exhibits)

@app.route("/tickets", methods=["GET", "POST"])
def tickets():
    if request.method == "GET":
        # show the form for the user to add 'order a ticket'
        today = datetime.now().strftime("%Y-%m-%d") #sample 2025-03-20
        return render_template("ticketform.html", today=today)
    else: # the POST request i.e. they filled out the form
        ticket_order = request.form
        if not session.get("cart"): # if there is not a cart already started
            session["cart"] = []
        session["cart"].append(ticket_order) # add the ticket order to teh cart
        flash(f"Your tickets have been added to the cart.")
        return redirect("/")

@app.route("/cart")
def show_cart():
    # check to see if there is a cart
    if not session.get("cart"):
        flash("Your cart is empty, add some tickets.")
        return redirect("/tickets")
    else:
        return render_template("cart.html")

@app.route("/emptycart", methods=["GET","POST"])
def emptycart():
    if not session.get("cart"):
        flash("Your cart is empty, add some tickets.")
        return redirect("/tickets")
    else:
        if request.method == "GET":
            session["emptycart"] = True
        else:
            session.pop('cart') # clear out only the cart session element
            session.pop('emptycart')

        return redirect("/cart")

@app.route("/checkout")
def checkout():
    # show a confirmation page
    # skip for now - but similar to the empty cart modal

    # add the ticket order to the database.
    completed_orders = []
    ticket_order = session.get('cart', None)
    if not ticket_order:
        flash("You have nothing in your cart.")
        return redirect("/tickets")
    else:
        for ticket in ticket_order:
            order_id = q.add_ticket_order(ticket)
            completed_orders.append(order_id)
        if len(completed_orders) > 0:
            session.pop("cart")
            # session.pop("emptycart")
        flash(f"Your tickets have been ordered")
        return redirect("/")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
