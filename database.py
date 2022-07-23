from deta import Deta

key = 'c02b0rap_raU7wvNb1haRR4osTbCivV8gcDiaFpgG'

# Initialize app with deta key
deta = Deta(key)

# Create/Connect to the database
db = deta.Base("users_db")


# Function to add user
def insert_users(username, name, password):
    return db.put({"key": username, "name": name, "password": password})


def fetch_users():
    res = db.fetch()
    return res.items
