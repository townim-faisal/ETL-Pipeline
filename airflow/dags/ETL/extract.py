# import mysql
import mysql.connector
import pandas as pd, time
import datetime, os, sys
from dotenv import load_dotenv
import yaml
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent.absolute()
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

root_dir = Path(__file__).parent.absolute()
param_file_name = os.path.join(root_dir,'config.yaml')

"""
Extract data from Source DB in between two time range
Return: list of order status, list of food ordered belongs to those orders
"""

def extract_data_from_source(time1='2022-01-26 00:00:01', time2=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    # try:
        print('Time range:', time1, time2)
        with open(param_file_name, "r") as config_file:
            params = yaml.safe_load(config_file)
        # print("Parameters:", params)
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('SOURCE_DB_PORT'),
            user='root',
            password=os.getenv('SOURCE_DB_ROOT_PASSWORD'),
            database=os.getenv('SOURCE_DB_DATABASE')
        )

        cursor = db.cursor()
        cursor.execute("SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
        cursor.execute("SET GLOBAL sql_mode = 'NO_ENGINE_SUBSTITUTION';")

        # GET the order status with how much sale with restaurant info
        order_query = f"""select ord.id as order_id, sum(ford.total_amount) as total_sale, count(ford.food_id) as total_quantity, 
        ost.status as order_completed, ord.dest_thana,
        ord.dest_city, res.name as restaurant_name, res.thana as restaurant_thana, res.city as restaurant_city, 
        ost.order_time, ost.cooking_finished_time, ost.rider_pickup_time, ost.delivered_time, ost.customer_feedback, 
        ost.customer_food_rating, ost.customer_delivery_rating 
        from orders ord 
        INNER JOIN order_status ost ON ord.id=ost.order_id 
        LEFT JOIN restaurants res ON res.id=ord.restaurants_id 
        LEFT JOIN food_order ford ON ord.id=ford.order_id 
        WHERE ford.order_id IN 
        (select order_id from order_status where order_time BETWEEN '{time1}' AND '{time2}')
        GROUP by ford.order_id;"""
        cursor.execute(order_query)
        order_values = cursor.fetchall()
        time.sleep(2)
        columns = [desc[0] for desc in cursor.description]
        order_values = pd.DataFrame(order_values, columns=columns)
        
        # print(food_values)

        # GET the food info with restaurant info for particualr order with how much customer paid and how much food ordered
        food_order_query = f"""select ford.order_id, ford.number_of_food, f.name as food_name, f.price as food_price, 
        f.type as food_type, res.name as res_name, res.thana as res_thana, res.city as res_city, 
        ford.total_amount as total_amount_of_food from food_order ford 
        LEFT JOIN foods f ON f.id=ford.food_id LEFT JOIN restaurants res on res.id=f.restaurant_id
        WHERE ford.order_id IN 
        (select order_id from order_status 
        where order_time BETWEEN '{time1}' AND '{time2}');"""
        cursor.execute(food_order_query)
        food_order_values = cursor.fetchall()
        time.sleep(2)

        columns = [desc[0] for desc in cursor.description]
        # print(columns)
        food_order_values = pd.DataFrame(food_order_values, columns=columns)

        cursor.close()
        db.close()

        print('Total number of orders extracted:', len(order_values), 'from', time1, 'to', time2)

        order_values.to_csv(os.path.join(root_dir,params['extacted_order_data_file_name']), index=False)
        food_order_values.to_csv(os.path.join(root_dir,params['extacted_food_order_data_file_name']), index=False)
    
    # except Exception as e:
    #     print(e)
    #     print('Error has been occured!...')
    #     # return None, None



if __name__ == "__main__":
    extract_data_from_source(time1='2022-01-26 00:00:01',time2=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
