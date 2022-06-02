DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

CREATE TABLE IF NOT EXISTS dim_location(
    id BIGSERIAL PRIMARY KEY,
    thana VARCHAR(26) not null UNIQUE,
    city VARCHAR(26) not null
);

CREATE TABLE IF NOT EXISTS dim_restaurant(
    id BIGSERIAL PRIMARY KEY,
    restaurant_name VARCHAR(256) not null,
    location_id BIGINT references dim_location(id)
);

CREATE TABLE IF NOT EXISTS dim_food_type(
    id BIGSERIAL PRIMARY KEY,
    type_name VARCHAR(256) not null UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_food(
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(256) not null,
    price INT not null,
    type_id BIGINT references dim_food_type(id),
    restaurant_id BIGINT references dim_restaurant(id)
);


CREATE TABLE IF NOT EXISTS dim_time(
    id TIME PRIMARY KEY,
    hour INT not null,
    minute INT not null
);


CREATE TABLE IF NOT EXISTS dim_date(
    id DATE PRIMARY KEY,
    -- date DATE not
    day_name VARCHAR(26) not null,
    month_name VARCHAR(26) not null,
    year_no INT,
    week_in_year INT
);

INSERT INTO dim_location (thana, city) VALUES ('Mirpur', 'Dhaka');
INSERT INTO dim_location (thana, city) VALUES ('Dhanmondi', 'Dhaka');
INSERT INTO dim_location (thana, city) VALUES ('Banani', 'Dhaka');
INSERT INTO dim_location (thana, city) VALUES ('Uttara', 'Dhaka');

INSERT INTO dim_food_type (type_name) VALUES ('pizza');
INSERT INTO dim_food_type (type_name) VALUES ('burger');
INSERT INTO dim_food_type (type_name) VALUES ('chinese');
INSERT INTO dim_food_type (type_name) VALUES ('biriyani');


CREATE TABLE IF NOT EXISTS fact_order(
    id BIGSERIAL PRIMARY KEY,
    delivered_to_id BIGINT references dim_location(id) not null,
    restaurant_id BIGINT references dim_restaurant(id) not null,
    ordered_on_date_id DATE references dim_date(id) not null,
    ordered_at_time_id TIME references dim_time(id) not null,
    rider_pickup_on_date_id DATE references dim_date(id),
    rider_pickup_at_time_id TIME references dim_time(id),
    cooking_finished_on_date_id DATE references dim_date(id),
    cooking_finished_at_time_id TIME references dim_time(id),
    food_delivered_on_date_id DATE references dim_date(id),
    food_delivered_at_time_id TIME references dim_time(id),
    order_completed BOOLEAN,
    total_price INT,
    customer_feedback TEXT,
    customer_food_rating INT,
    customer_rider_rating INT
);

CREATE TABLE IF NOT EXISTS dim_food_order(
    order_id BIGINT not null references fact_order(id),
    food_id BIGINT not null references dim_food(id),
    quantity INT not null,
    amount_charged INT not null
);

-- find or insert location by thana and city
create or replace function find_location_id(thana_name VARCHAR(26), city_name VARCHAR(26))
returns BIGINT
language plpgsql
as $$
declare
   location_id BIGINT;
begin
  select id into location_id from dim_location where thana = thana_name and city = city_name;
  if not found then
     insert into dim_location (thana, city) values (thana_name, city_name) returning id into location_id;
  end if;
  return location_id;
end;$$;

-- find or insert restaurant id based on restaurant thana, name, city
create or replace function find_restaurant_id(res_name VARCHAR(256), thana_name VARCHAR(26), city_name VARCHAR(26))
returns BIGINT
language plpgsql
as $$
declare
   restaurant_id BIGINT;
begin
  select id into restaurant_id from dim_restaurant 
  where restaurant_name=res_name 
  and location_id=find_location_id(thana_name,city_name);
  if not found then
     insert into dim_restaurant (restaurant_name, location_id) 
	 values (res_name, find_location_id(thana_name,city_name)) 
	 returning id into restaurant_id;
  end if;
  return restaurant_id;
end;$$;

-- find time by given timestamp
create or replace function find_time_id(timest timestamp)
returns TIME
language plpgsql
as $$
declare
   time_id TIME;
begin
  select id into time_id from dim_time 
  where hour=(select extract(hour from timest)) and minute=(select extract(minute from timest));
  
  if not found then
     insert into dim_time (id, hour, minute) 
	 values (timest::time, (select extract(hour from timest)), 
			 (select extract(minute from timest)) ) 
	 returning id into time_id;
  end if;
  return time_id;
end;$$;

-- find date id by timestamp
create or replace function find_date_id(timest timestamp)
returns DATE
language plpgsql
as $$
declare
   date_id DATE;
begin
  select id into date_id from dim_date
  where id=(select timest::date);
  if not found then
     insert into dim_date (id, day_name, month_name, year_no, week_in_year) 
	 values (timest::date, (select TO_CHAR(timest, 'day')), 
			 (select TO_CHAR(timest, 'month')),
			 (select extract(year from timest)),
			 (select extract(week from timest))
			) 
	 returning id into date_id;
  end if;
  return date_id;
end;$$;

-- find food id by restaurant
create or replace function find_or_update_food_id(food_name VARCHAR(256), food_type VARCHAR(256), food_price INT, 
res_name VARCHAR(256), res_thana VARCHAR(26), res_city VARCHAR(26))
returns BIGINT
language plpgsql
as $$
declare
   food dim_food%rowtype;
   food_type_id BIGINT;
begin
  select id into food_type_id from dim_food_type where type_name=food_type;
  -- insert as food type not found
  if not found then
    insert into dim_food_type (type_name) values(food_type) returning id into food_type_id;
  end if;
  select id from dim_food into food
  where name=food_name and restaurant_id=find_restaurant_id(res_name,res_thana,res_city)
  and type_id=food_type_id;
  -- insert as food not found
  if not found then 
    insert into dim_food (name, price, type_id, restaurant_id) 
    values (food_name, food_price, food_type_id, find_restaurant_id(res_name,res_thana,res_city)) 
    returning * into food;
  else
    if food.price<>food_price then
      update dim_food
      SET price = food_price
      WHERE id = food.id
      returning * into food;
    end if;
  end if;
  return food.id;
end;$$;