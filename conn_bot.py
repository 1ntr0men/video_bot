from db import DB, Users

db = DB()
users = Users(db.get_connection())
users.init_table()
users.insert(12345678)
users.non_subscribe(12345678)
print(users.get_all())
print(users.exists(1234567)[1])
