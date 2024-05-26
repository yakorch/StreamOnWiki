CREATE KEYSPACE IF NOT EXISTS wikipedia WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 2 };

USE wikipedia;


CREATE TABLE IF NOT EXISTS unique_domains (
    domain TEXT PRIMARY KEY,
);


CREATE TABLE IF NOT EXISTS user_pages (
    user_id INT,
    page_id INT,
    PRIMARY KEY ((user_id), page_id)
);

CREATE TABLE IF NOT EXISTS page_information (
    page_id INT,
    uri TEXT,
    title TEXT,

    PRIMARY KEY (page_id)
);

CREATE TABLE IF NOT EXISTS domain_pages (
    domain TEXT,
    num_pages COUNTER,
    PRIMARY KEY ((domain))
);


CREATE TABLE IF NOT EXISTS active_users_by_date (
    date DATE,
    user_id INT,
    user_name TEXT,
    num_created_pages COUNTER,
    PRIMARY KEY ((date), user_id, user_name)
);