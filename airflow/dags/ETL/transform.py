import pandas as pd, random, names, string, time, numpy as np
import datetime, os, sys
import json, yaml
from pathlib import Path

root_dir = Path(__file__).parent.absolute()
param_file_name = os.path.join(root_dir,'config.yaml')

def transform_data():
    with open(param_file_name, "r") as config_file:
        params = yaml.safe_load(config_file)
    order_values, food_order_values = None, None
    params['extacted_order_data_file_name']=os.path.join(root_dir,params['extacted_order_data_file_name'])
    params['extacted_food_order_data_file_name']=os.path.join(root_dir,params['extacted_food_order_data_file_name'])
    if os.path.exists(params['extacted_order_data_file_name']) and os.path.exists(params['extacted_food_order_data_file_name']):
        order_values = pd.read_csv(params['extacted_order_data_file_name'])
        food_order_values = pd.read_csv(params['extacted_food_order_data_file_name'])
    
    if order_values is not None and food_order_values is not None:
        order_values.reset_index(drop=True, inplace=True)
        food_order_values.reset_index(drop=True, inplace=True)

        orders = {}
        for index, row in order_values.iterrows():
            order_id = row['order_id']
            if order_id not in orders:
                orders[order_id] = {}
                orders[order_id]['order_status'] = None
                orders[order_id]['foods'] = []
            # print(orders)
            
            orders[order_id]['order_status'] = (
                row['dest_thana'], row['dest_city'], 
                row['restaurant_name'], row['restaurant_thana'], row['restaurant_city'],
                row['order_time'], row['order_time'],
                row['rider_pickup_time'], row['rider_pickup_time'],
                row['cooking_finished_time'], row['cooking_finished_time'],
                row['delivered_time'], row['delivered_time'],
                bool(row['order_completed']), row['total_sale'], 
                row['customer_feedback'], row['customer_food_rating'], row['customer_delivery_rating']
            )

            current_order_foods = food_order_values.loc[food_order_values['order_id'] == order_id]

            for index2, row2  in current_order_foods.iterrows():
                amount_charged = int(row2['total_amount_of_food'])*int(row2['food_price'])
                orders[order_id]['foods'].append(
                    [row2['food_name'], row2['food_type'], row2['food_price'], 
                    row2['res_name'], row2['res_thana'], row2['res_city'], 
                    row2['total_amount_of_food'], amount_charged]
                )
        
        print('Total orders transformed:', len(list(orders.keys())))

        with open(os.path.join(root_dir,params['transformed_data_file_name']), 'w') as fp:
            json.dump(orders, fp, indent=4)

        os.remove(params['extacted_order_data_file_name'])
        os.remove(params['extacted_food_order_data_file_name'])

    else:
        print('Tranformation failed!...')



if __name__ == "__main__":
    from extract import extract_data_from_source
    extract_data_from_source(time1='2022-01-26 00:00:01',
                    time2=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    transform_data()
