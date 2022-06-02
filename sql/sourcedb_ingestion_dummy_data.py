import mysql.connector
import pandas as pd, random, names, string, time, os, sys
import datetime

letters = string.ascii_lowercase
full_names = []
for i in range(200):
    full_names.append(names.get_full_name())

restaurant_cuisine_lists = {
    'pizza' : ['Cheeze','Pizza Hut', 'Pizza Inn'],
    'burger': ['Burger King','Burger Xpress','Chillox'],
    'chinese': ['Yum Cha', 'Imperial Wok'],
    'biriyani': ['Kacchi Bhai', 'Sultans Dine']
}

thanas = ['Mirpur', 'Dhanmondi', 'Banani', 'Uttara']
cities = ['Dhaka']

restaurant_owners = full_names[:10]
riders = full_names[10:20]
customers = full_names[20:]


conn = mysql.connector.connect(
  host='localhost',
  port='3306',
  user='root',
  password=''
)

print(conn)

cursor = conn.cursor()
cursor.execute('CREATE DATABASE IF NOT EXISTS sourcedb CHARACTER SET utf8 COLLATE utf8_general_ci;')
cursor.close() 


db = mysql.connector.connect(
  host='localhost',
  port='3306',
  user='root',
  password='',
  database='sourcedb'
)

cursor = db.cursor()

with open('sourcedb.sql') as f:
    cursor.execute(f.read(), multi=True)

time.sleep(5)
cursor.close()
db.close()


"""
EMPTY ALL TABLE
"""
db = mysql.connector.connect(
  host='localhost',
  port='3306',
  user='root',
  password='',
  database='sourcedb'
)
cursor = db.cursor()
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE foods;")
# time.sleep(3)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE food_order;")
# time.sleep(3)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE orders;")
# time.sleep(3)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE order_status;")
# time.sleep(3)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE restaurants;")
# time.sleep(3)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE users;")
# time.sleep(3)
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")


"""
USER TABLE
"""
user_values = []

for i in restaurant_owners:
    random.seed(random.randint(1,999))
    first_name = i.split(' ')[0]
    last_name = i.split(' ')[1]
    email = f'{first_name}.{last_name}@gmail.com'.lower()
    nid = random.randint(100000,999999)
    phone_number = '+8801'+str(random.randint(1111111,9999999))
    address = ''.join(random.choice(letters) for _ in range(20))
    for _ in range(random.randint(1,5)):
        j = random.randint(4,15)
        address = address.replace(address[j],' ')
    city = cities[0]
    random.shuffle(thanas)
    thana = random.choices(thanas)[0]
    user_type = 'owner'
    # created_at = datetime.now().timestamp()
    user_values.append((first_name, last_name, email, address, city, thana, nid, phone_number, user_type))
for i in riders:
    random.seed(random.randint(1,999))
    first_name = i.split(' ')[0]
    last_name = i.split(' ')[1]
    email = f'{first_name}.{last_name}@gmail.com'.lower()
    nid = random.randint(100000,999999)
    phone_number = '+8801'+str(random.randint(1111111,9999999))
    address = ''.join(random.choice(letters) for _ in range(20))
    for _ in range(random.randint(1,5)):
        j = random.randint(4,15)
        address = address.replace(address[j],' ')
    city = cities[0]
    random.shuffle(thanas)
    thana = random.choices(thanas)[0]
    user_type = 'rider'
    # created_at = datetime.now().timestamp()
    user_values.append((first_name, last_name, email, address, city, thana, nid, phone_number, user_type))
for i in customers:
    random.seed(random.randint(1,999))
    first_name = i.split(' ')[0]
    last_name = i.split(' ')[1]
    email = f'{first_name}.{last_name}@gmail.com'.lower()
    nid = random.randint(100000,999999)
    phone_number = '+8801'+str(random.randint(1111111,9999999))
    address = ''.join(random.choice(letters) for _ in range(20))
    for _ in range(random.randint(1,5)):
        j = random.randint(4,15)
        address = address.replace(address[j],' ')
    city = cities[0]
    random.shuffle(thanas)
    thana = random.choices(thanas)[0]
    user_type = 'customer'
    # created_at = datetime.now().timestamp()
    user_values.append((first_name, last_name, email, address, city, thana, nid, phone_number, user_type))

# print(user_values)
user_query = "INSERT INTO users (first_name, last_name, email, address, city, thana, nid, phone_number, type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
cursor.executemany(user_query, user_values)
db.commit()
print(cursor.rowcount, "records inserted")
time.sleep(3)
# cursor.close()
# db.close()


"""
RESTAURANT & FOOD TABLE
"""
restaurant_values = []
food_values = []
restaurant_owners_id = [i+1 for i in range(10)]
owner_index, res_index = 0, 0

for key, val in restaurant_cuisine_lists.items():
    random.seed(random.randint(1,999))
    status = 1
    for i in val:
        # restaurant value
        restaurant_name = i
        owner_id = restaurant_owners_id[owner_index]
        phone_number = '+8801'+str(random.randint(1111111,9999999))
        address = ''.join(random.choice(letters) for _ in range(20))
        for _ in range(random.randint(1,5)):
            j = random.randint(4,15)
            address = address.replace(address[j],' ')
        city = cities[0]
        random.shuffle(thanas)
        thana = random.choices(thanas)[0]
        restaurant_values.append((owner_id, restaurant_name, city, address, thana, phone_number))
        res_index+=1
        # food values
        for f in range(random.randint(5,20)):
            food_name = ''.join(random.choice(letters) for _ in range(random.randint(7,10)))
            food_name = food_name.replace(address[random.randint(2, len(food_name)-2)],' ')
            price = random.randint(50, 500)
            food_type = key
            food_values.append((res_index, food_name, food_type, price))
        owner_index+=1
    
# print(restaurant_values, food_values)
# db = mysql.connector.connect(
#   host='localhost',
#   port='3306',
#   user='root',
#   password='',
#   database='sourcedb'
# )
# cursor = db.cursor()
restaurant_query = "INSERT INTO restaurants (owner_id, name, city, address, thana, phone_number) VALUES (%s, %s, %s, %s, %s, %s);"
food_query = "INSERT INTO foods (restaurant_id, name, type, price) VALUES (%s, %s, %s, %s);"
cursor.executemany(restaurant_query, restaurant_values)
db.commit()
print(cursor.rowcount, "records inserted")
time.sleep(3)
cursor.executemany(food_query, food_values)
db.commit()
print(cursor.rowcount, "records inserted")
time.sleep(3)

"""
ORDERS, FOOD ORDER and ORDER STATUS TABLE
"""
customers = user_values[20:]
number_of_customers = len(customers)
order_query = "INSERT INTO orders(restaurants_id, ordered_by_id, pickup_rider_id, dest_address, dest_thana, dest_city) VALUES (%s, %s, %s, %s, %s, %s);"
food_order_query = "INSERT INTO food_order(order_id, food_id, number_of_food, total_amount) VALUES (%s, %s, %s, %s);"
order_status_query = "INSERT INTO order_status(order_id, status, order_time, cooking_finished_time, rider_pickup_time, delivered_time, customer_feedback, customer_food_rating, customer_delivery_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"


# start from januar 1, 2021 to 
def random_time_generator():
    start_date = datetime.date(2021, 1, 1) # (year, month, day) t
    end_date = datetime.datetime.now().date()
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    
    random_hour = random.randrange(24)
    random_minute = random.randrange(60)
    
    random_date = str(random_date).split('-')
    start_time = datetime.datetime(int(random_date[0]), int(random_date[1]), int(random_date[2]), random_hour, random_minute)
    # end_time = start_time + datetime.timedelta(minutes=random.randrange(15,60))
    return start_time



restaurants_info = {}
food_index = 1
# print(food_values)
for f in food_values:
    res_index, food_name, food_type, price = f
    if res_index not in restaurants_info:
        restaurants_info[res_index] = {}
        restaurants_info[res_index]['food_indexes'] = [food_index]
        restaurants_info[res_index]['food_infos'] = [f]
    else:
        restaurants_info[res_index]['food_indexes'].append(food_index)
        restaurants_info[res_index]['food_infos'].append(f)
    food_index+=1
# print(restaurants_info)
# sys.exit()

order_number = 0
while order_number<=5000:
    random.seed(random.randint(100,10000))

    # order in restaurant
    dest_address = ''.join(random.choice(letters) for _ in range(20))
    for _ in range(random.randint(1,5)):
        j = random.randint(4,15)
        dest_address = dest_address.replace(dest_address[j],' ')
    random.shuffle(thanas)
    dest_thana = random.choices(thanas)[0]
    dest_city = cities[0]
    # random.shuffle(food_values)
    index = random.randint(0, len(food_values)-1)
    restaurant_id, _, _, _ = food_values[index]
    ordered_by_id = random.randint(21,number_of_customers)
    pickup_rider_id = random.randint(10,10+len(riders))
    cursor.execute(order_query, (restaurant_id, ordered_by_id, pickup_rider_id, dest_address, dest_thana, dest_city))
    db.commit()
    order_number+=1
    time.sleep(2)

    # order for food
    food_ids = restaurants_info[restaurant_id]['food_indexes']
    food_infos = restaurants_info[restaurant_id]['food_infos']  
    # print(food_ids, food_infos)  
    total_order_food = random.randint(1,5)    
    ids = [i for i in range(len(food_ids))]
    random.shuffle(ids)
    # print(ids)
    # break
    for i in range(total_order_food):        
        fid = random.randint(0, len(ids)-1)
        _, _, _, price = food_infos[fid]
        food_id = food_ids[fid]
        number_of_food = random.randint(1,3)
        total_amount = price*number_of_food
        cursor.execute(food_order_query, (order_number, food_id, number_of_food, total_amount))
        db.commit()
        time.sleep(2)
        # print('order res_id:', (restaurants_id))
        # print('food order:', (food_id, number_of_food, total_amount))
    
    # if order_number>=2:
    #     break
    
    # order status
    status = True
    order_time = random_time_generator()
    cooking_finished_time = order_time + datetime.timedelta(minutes=random.randrange(15,70))
    rider_pickup_time = cooking_finished_time + datetime.timedelta(minutes=random.randrange(20))
    delivered_time = rider_pickup_time + datetime.timedelta(minutes=random.randrange(8,40))
    customer_food_rating = random.randint(1,5)
    customer_delivery_rating = random.randint(1,5)
    customer_feedback = ''.join(random.choice(letters) for _ in range(50))
    for _ in range(random.randint(1,20)):
        j = random.randint(4,15)
        customer_feedback = customer_feedback.replace(customer_feedback[j],' ')
    cursor.execute(order_status_query, (order_number, status, str(order_time), str(cooking_finished_time), str(rider_pickup_time), str(delivered_time), customer_feedback, customer_food_rating, customer_delivery_rating))
    db.commit()
    print('Order No:', order_number)
    time.sleep(2)

cursor.close()
db.close()