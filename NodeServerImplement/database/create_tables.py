import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'dbname': 'warehouse_9',
    'user': 'postgres',
    'password': 'superuser@9',
    'host': 'localhost',
    'port': 5432
} 

SQL_SCRIPT = """
CREATE TABLE super_UserAgent(
    id uuid primary key,
    name varchar(255) not null
);

CREATE TABLE user_Manager(
    id uuid primary key,
    name varchar(255) not null,
    cpf varchar(20),
    salary NUMERIC,
    email varchar(255),
    phone varchar(15),
    hiring_date DATE
);

CREATE TABLE user_Requester(
    id uuid primary key,
    name varchar(255),
    cpf varchar(20),
    salary numeric,
    email varchar(255),
    phone varchar(15),
    hiring_date DATE
);

CREATE TABLE user_Accountancy(
    id uuid primary key,
    name varchar(255),
    cpf varchar(20),
    salary numeric,
    email varchar(255),
    phone varchar(15),
    hiring_date DATE
);

CREATE TABLE person_Responsible(
    id uuid primary key,
    name varchar(255) not null,
    cpf varchar(20),
    salary numeric,
    email varchar(255),
    phone varchar(15),
    hiring_date DATE
);

CREATE TABLE locals_Table(
    id uuid primary key,
    name_local varchar(255),
    street varchar(255),
    building_number INT,
    id_responsible_fk uuid references person_Responsible(id)
);

CREATE TABLE item_Table(
    id uuid primary key,
    request_id_fk uuid references request_Table(id_request),
    name varchar(255),
    color varchar(50)
);

CREATE TABLE request_Table(
    id_request uuid primary key,
    id_manager_fk uuid references user_Manager(id),
    id_requester_fk uuid references user_Requester(id),
    num_period int,
    item varchar(255),
    quantity int,
    unit_value numeric,
    total_value numeric,
    data_requested date
);

CREATE TABLE shipping_Table(
    id uuid primary key,
    id_request_fk uuid references request_Table(id_request),
    id_manager_fk uuid references user_Manager(id),
    id_locals_fk uuid references locals_Table(id)
);

CREATE TABLE received_Table(
    id uuid primary key,
    id_request_fk uuid references request_Table(id_request),
    name_responsible_fk uuid references person_Responsible(id),
    data_received date
);

CREATE TABLE month_Quote(
    id uuid primary key,
    fk_requester uuid references user_Requester(id),
    year int,
    month int,
    balance numeric
);
"""


def create_tables():
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:  # executing the sql script
        for statement in SQL_SCRIPT.split(";"):
            if statement.strip():  # ignore null statements
                cursor.execute(statement)

        print("TABLES ARE SUCCESSFUL CREATED")
    except Exception as e:
        print(f'ERROR: {e}')
    finally:
        if connection:
            cursor.close()
            connection.close()


if __name__ == '__main__':
    create_tables()
