from flask import Flask, render_template, request, redirect, session, abort, flash
from flask_session import Session
from datetime import datetime
# bring in the queries functions
import queries as q

app = Flask(__name__)
app.config["SESSION_TYPE"] = "cachelib"
app.config["SESSION_PERMANENT"] = False
Session(app)
# add this for message flashing
app.secret_key = "hello"

@app.route("/")
def index():
    # get the exhibit names from the database
    exhibits_list = q.get_exhibit_names()
    return render_template("index.html", exhibits=exhibits_list)

@app.post("/exhibits")
def exhibits():
    # get the name from the form
    exhibit_name = request.form.get("exhibit-name")
    # set the session for exhibit
    session["exhibit"] = exhibit_name
    flash(f"I will remember this choice: {exhibit_name}")
    # use the name to query the database
    exhibit_details = q.get_exhibit_details(exhibit_name)
    if not exhibit_details:
        abort(404)
    else:
        return render_template("exhibits_detail.html", exhibit=exhibit_details)


@app.route("/animals/<exhibit>")
def animals(exhibit):
    animals_list = q.get_animals_by_exhibit(exhibit)
    return render_template("exhibit_animals.html", animals_list=animals_list)


@app.route("/animals")
def show_animals():
    if session.get("exhibit"): # has an exhibit been selected from the user
        return redirect(f"/animals/{session.get('exhibit')}")
    else:
        return redirect("/")

@app.route("/animals/<int:animal_id>")
def show_animal_details(animal_id):
    # get the details for the animal from the database
    animal_details = q.get_animal_details(animal_id)
    if animal_details:
        # create an html template page that has the animal details
        # displayed
        return render_template("animal_details.html", animal=animal_details)
    else:
        abort(404)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET":
        # show the form
        exhibits = q.get_exhibit_names()
        return render_template("add.html", exhibits=exhibits)
    else: # POST request
        # process the form data
        animal = {
            "species": request.form.get("species"),
            "diet": request.form.get("diet"),
            "habitat": request.form.get("habitat"),
            "population": int(request.form.get("population")),
            "description": request.form.get("description"),
            "exhibit": request.form.get("exhibit")
        }
        animal_id = q.add_animal(animal) # animal is a dict
        if animal_id > 0:
            flash(f"The {animal.get('species')} was added to the database!")
        return redirect(f"/animals/{animal_id}")


@app.route("/tickets", methods=["GET", "POST"])
def tickets():
    if request.method == "GET": # the user clicked on the link
        #show the ticket order form
        today = datetime.now().strftime("%Y-%m-%d") # sample '2025-03-20'
        return render_template("ticketform.html", today=today)
    else: # the POST --> the user filled out the form
        ticket_order = request.form
        if not session.get('cart'): # if there isn't a cart already
            session['cart'] = []
        # add the ticket order to the cart
        session['cart'].append(ticket_order)
        flash(f"Your {ticket_order.get('number-of-tickets')} ticket(s) were added to the cart.")
        return redirect("/")

@app.route("/cart")
def show_cart():
    # first check to see if there is a cart
    if not session.get('cart'):
        flash("Your cart is empty, order tickets here.")
        return redirect("/tickets")
    else:
        return render_template("cart.html")


@app.route("/emptycart", methods=["GET","POST"])
def emptycart():
    #check to make sure there is a cart (this is done in the /cart route)
    if request.method == "GET":
        session['emptycart'] = True
    else: # they want to empty the cart
        # empty the cart
        session.pop("cart") # this will remove only the cart session variable
        session.pop("emptycart")
    return redirect("/cart")

@app.route("/checkout")
def chekout():
    # show a confirmation page similar to emptycart (take in payment though)
    # skipped for this example

    completed_orders = []
    #add our order to the database
    ticket_orders = session.get('cart', None)
    if not ticket_orders:
        flash("You have nothing in your cart. Add some tickets now.")
        return redirect("/tickets")
    else:
        for ticket in ticket_orders:
            order_num = q.add_ticket_order(ticket)
            completed_orders.append(order_num)
        if len(completed_orders) > 0:
            flash(f"Your tickets have been ordered {completed_orders}")
            session.pop('cart')
            return redirect("/")
        else:
            flash("Somethine whent wrong with you order. Contact the Zoo Ticket office.")
            return redirect("/tickets")



@app.errorhandler(404)
def page_not_found(e):
    return render_template("page_not_found.html")

