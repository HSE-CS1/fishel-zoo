from cs50 import SQL
from secrets import token_hex

#connect to the databse
db = SQL("sqlite:///fishelzoo.db")

def get_exhibit_names():
    sql = "SELECT name FROM exhibits ORDER BY name"
    results = db.execute(sql)
    return results

def get_exhibit_details(name):
    sql = "SELECT * FROM exhibits WHERE name = ?"
    results = db.execute(sql, name)
    if len(results) == 1:
        return results[0]  # give back just the dictionary
    else:
        return None

def get_animals_by_exhibit(name):
    sql = "SELECT * FROM animals WHERE exhibit = ? ORDER BY species"
    results = db.execute(sql, name)
    if len(results) == 0:
        return None
    else:
        return results


def get_animal_details(id):
    sql = "SELECT * FROM animals WHERE id = ?"
    results = db.execute(sql, id)
    if len(results) != 1:
        return None
    else:
        return results[0] # just the dictionary



def add_animal(animal): #animal is a dictionary
    sql = "INSERT INTO animals (species, diet, habitat, description, population, exhibit) VALUES (?, ?, ?, ?, ?, ?)"
    animal_id = db.execute(sql, animal.get("species"),
                              animal.get("diet"),
                              animal.get("habitat"),
                              animal.get("description"),
                              animal.get("population"),
                              animal.get("exhibit")
                              )
    return animal_id

def add_ticket_order(ticket):
    sql = "INSERT INTO tickets (name, contact, visit_date, num_tickets, confirmation) VALUES (?,?,?,?,?)"
    name = ticket.get("visitor-name")
    contact = ticket.get("visitor-contact")
    visit_date = ticket.get("visit-date")
    num_tickets = ticket.get("number-of-tickets")
    confirmation = token_hex(5) # secure random token
    order_num = db.execute(sql, name, contact, visit_date, num_tickets, confirmation)
    return order_num






