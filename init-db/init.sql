CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    weather VARCHAR(200),
    essentials TEXT
);

CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id),
    role VARCHAR(20),
    message TEXT,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);