import mysql.connector
import pandas as pd, random, names, string, time
import datetime, os, sys
from dotenv import load_dotenv
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent.absolute()
# print(root_dir)
# sys.exit()
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

letters = string.ascii_lowercase
thanas = ['Mirpur', 'Dhanmondi', 'Banani', 'Uttara']
cities = ['Dhaka']

def get_db():
    print(os.getenv('SOURCE_DB_PORT'))
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=3305,
        user='root',
        password=os.getenv('SOURCE_DB_ROOT_PASSWORD'),
        database=os.getenv('SOURCE_DB_DATABASE')
    )

db = get_db()
cursor = db.cursor()
query = "SELECT id, restaurant_id, price FROM foods;"
cursor.execute(query)
food_values = cursor.fetchall()
# sys.exit()

query = "SELECT * FROM users where type='customer';"
cursor.execute(query)
customers = cursor.fetchall()


"""
ORDERS, FOOD ORDER and ORDER STATUS TABLE
"""
# customers = users[20:]
number_of_customers = len(customers)
order_query = "INSERT INTO orders(restaurants_id, ordered_by_id, pickup_rider_id, dest_address, dest_thana, dest_city) VALUES (%s, %s, %s, %s, %s, %s);"
food_order_query = "INSERT INTO food_order(order_id, food_id, number_of_food, total_amount) VALUES (%s, %s, %s, %s);"
order_status_query = "INSERT INTO order_status(order_id, status, order_time, cooking_finished_time, rider_pickup_time, delivered_time, customer_feedback, customer_food_rating, customer_delivery_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"

def random_time_generator():
    start_date = datetime.date(2021, 1, 1) # (year, month, day) t
    end_date = datetime.datetime.now().date()
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    
    random_hour = random.randrange(24)
    random_minute = random.randrange(60)
    
    # no random date will be here, date will be today
    random_date = str(end_date).split('-')
    start_time = datetime.datetime(int(random_date[0]), int(random_date[1]), int(random_date[2]), random_hour, random_minute)
    # end_time = start_time + datetime.timedelta(minutes=random.randrange(15,60))
    return start_time



restaurants_info = {}
food_index = 1
for f in food_values:
    food_id, res_index, price = f
    if res_index not in restaurants_info:
        restaurants_info[res_index] = {}
        restaurants_info[res_index]['food_indexes'] = [food_index]
        restaurants_info[res_index]['food_infos'] = [f]
    else:
        restaurants_info[res_index]['food_indexes'].append(food_index)
        restaurants_info[res_index]['food_infos'].append(f)
    food_index+=1



# sys.exit()

total_delay_min = 10

def dummy_order_ingestion():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT MAX(id) FROM orders;"
    cursor.execute(query)
    order_number = cursor.fetchall()[0][0]
    print('Current order number:', order_number)

    order_number+=1
    # query = """select ord.id as order_id, sum(ford.total_amount) as total_sale, count(ford.food_id) as total_quantity, 
    #     ost.status as order_completed, ord.dest_thana,
    #     ord.dest_city, res.name as restaurant_name, res.thana as restaurant_thana, res.city as restaurant_city, 
    #     ost.order_time, ost.cooking_finished_time, ost.rider_pickup_time, ost.delivered_time, ost.customer_feedback, 
    #     ost.customer_food_rating, ost.customer_delivery_rating 
    #     from orders ord 
    #     INNER JOIN order_status ost ON ord.id=ost.order_id 
    #     LEFT JOIN restaurants res ON res.id=ord.restaurants_id 
    #     LEFT JOIN food_order ford ON ord.id=ford.order_id 
    #     WHERE ford.order_id IN 
    #     (select order_id from order_status where order_time BETWEEN '2022-01-01' AND '2022-06-20')
    #     GROUP by ord.id;"""
    # cursor.execute(query)
    # _ = cursor.fetchall()
    # time.sleep(2)

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
    _, restaurants_id, _ = food_values[index]
    ordered_by_id = random.randint(21, number_of_customers)
    pickup_rider_id = random.randint(10, 20)
    cursor.execute(order_query, (restaurants_id, ordered_by_id, pickup_rider_id, dest_address, dest_thana, dest_city))
    db.commit()
    time.sleep(2)

    # order for food
    food_ids = restaurants_info[restaurants_id]['food_indexes']
    food_infos = restaurants_info[restaurants_id]['food_infos']    
    total_order_food = random.randint(1,5)    
    ids = [i for i in range(len(food_ids))]
    random.shuffle(ids)
    for i in range(total_order_food):        
        fid = random.randint(0, len(ids)-1)
        _, _, price = food_infos[fid]
        food_id = food_ids[fid]
        number_of_food = random.randint(1,3)
        total_amount = price*number_of_food
        cursor.execute(food_order_query, (order_number, food_id, number_of_food, total_amount))
        db.commit()
        time.sleep(2)
    
    # order status
    status = True
    order_time = datetime.datetime.now() #random_time_generator()
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
    print('Order No:', order_number, 'is placed')
    # time.sleep(total_delay_min*60)
    time.sleep(2)

    cursor.close()
    db.close()