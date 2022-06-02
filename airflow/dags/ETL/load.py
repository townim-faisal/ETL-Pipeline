import psycopg2, datetime
import pandas as pd, random, names, string, time
import os, sys
import json, yaml
from dotenv import load_dotenv
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent.absolute()
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

root_dir = Path(__file__).parent.absolute()
param_file_name = os.path.join(root_dir,'config.yaml')


def load_data_to_target():
    # try:
        with open(param_file_name, "r") as config_file:
            params = yaml.safe_load(config_file)
        
        with open(os.path.join(root_dir,params['transformed_data_file_name']), 'r') as fp:
            orders = json.load(fp)

        db = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('TARGET_DB_PORT'),
            user=os.getenv('TARGET_DB_USER'),
            password=os.getenv('TARGET_DB_PASSWORD'),
            database=os.getenv('TARGET_DB_NAME')
        )
        cursor = db.cursor()

        order_query = """INSERT INTO fact_order (delivered_to_id, restaurant_id, ordered_on_date_id, ordered_at_time_id, 
                            rider_pickup_on_date_id, rider_pickup_at_time_id, 
                            cooking_finished_on_date_id, cooking_finished_at_time_id, 
                            food_delivered_on_date_id, food_delivered_at_time_id, 
                            order_completed, total_price, 
                            customer_feedback, customer_food_rating, customer_rider_rating)
                        VALUES
                            (find_location_id(%s, %s),
                            find_restaurant_id(%s, %s, %s),
                            find_date_id(%s),find_time_id(%s),
                            find_date_id(%s),find_time_id(%s),
                            find_date_id(%s),find_time_id(%s),
                            find_date_id(%s),find_time_id(%s),
                            %s,%s,%s,%s,%s) 
                        RETURNING id;"""

        food_order_query = """INSERT INTO dim_food_order (order_id, food_id, quantity, amount_charged)
                            VALUES (%s,find_or_update_food_id(%s, %s, %s, %s, %s, %s),%s,%s);"""

        for key in orders:
            order_status = orders[key]['order_status']
            food_orders = orders[key]['foods']
            cursor.execute(order_query, order_status)
            order_id = cursor.fetchone()[0]
            print('Order id:', order_id)
            db.commit()

            for food_order in food_orders:
                food_order.insert(0, order_id)
                food_order = tuple(food_order)
                cursor.execute(food_order_query, food_order)
                db.commit()
            
        cursor.close()
        db.close()
        os.remove(os.path.join(root_dir,params['transformed_data_file_name']))

        print('Total order loaded:', len(list(orders.keys())))

    # except Exception as e:
    #     print(e)
    #     print('Raise error in loading to target database!....') 

if __name__ == "__main__":
    load_data_to_target()
