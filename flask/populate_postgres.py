import psycopg2
import json

def create_sample_tables():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="apan5400",
        user="apan5400",
        password="apan5400"
    )
    cursor = conn.cursor()

    # Create sample tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10),
            price DECIMAL(10,2),
            volume INTEGER,
            date DATE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            location VARCHAR(100),
            temperature DECIMAL(5,2),
            rainfall DECIMAL(5,2),
            date DATE
        )
    """)

    # Insert sample data
    cursor.execute("""
        INSERT INTO stocks (symbol, price, volume, date) VALUES
        ('AAPL', 150.25, 1000000, '2023-01-01'),
        ('GOOGL', 2800.50, 500000, '2023-01-01'),
        ('MSFT', 300.75, 800000, '2023-01-01')
    """)

    cursor.execute("""
        INSERT INTO weather (location, temperature, rainfall, date) VALUES
        ('New York', 25.5, 0.0, '2023-01-01'),
        ('London', 15.2, 2.5, '2023-01-01'),
        ('Tokyo', 22.8, 0.0, '2023-01-01')
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Sample data inserted into PostgreSQL")

if __name__ == "__main__":
    create_sample_tables()