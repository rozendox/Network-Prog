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
    id uuid(255) primary key,
    name varchar(255),
    cpf varchar(20),
    salary numeric,
    email varchar(255),
    phone varchar(15),
    hiring_date DATE
);


CREATE TABLE user_Accountancy(
    id uuid(255) primary key,
    name varchar(255),
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
    id_responsible_fk uuid references person_Responsible
);

CREATE TABLE person_Responsible(
    id uuid primary key,
    name varchar(255) not null ,
    cpf varchar(20),
    salary numeric,
    email varchar(255),
    phone varchar(15),
    hiring_data date
);

CREATE TABLE item_Table(
    id uuid primary key ,
    /*fk do request a gente ainda n fez*/
    name varchar(255),
    color varchar(50)
);

CREATE TABLE request_Table(
    id_request uuid primary key,
    id_manager_fk uuid references user_Manager(id),
    id_requester_fk uuid references user_Requester(id),
    id_invoice_note int,
    num_period int,
    item varchar(255),
    quantity int,
    unit_value numeric,
    total_value numeric,
    data_requested date
);

CREATE TABLE shipping_Table(
    id uuid primary key,
    id_request_fk uuid references request_Table(id),
    id_manager_fk uuid references user_Manager(id),
    id_locals_fk uuid references locals_Table(id)
);

CREATE TABLE received_Table(
    id uuid primary key,
    id_request_fk uuid references request_Table(id),
    name_responsible_fk uuid references person_Responsible(id),
    data_received date
);

CREATE TABLE month_Quote(
    id uuid primary key,
    fk_requester uuid references user_requester(id),
    year int,
    month int,
    balance numeric
);