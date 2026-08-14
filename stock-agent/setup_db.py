from sqlalchemy import create_engine, text
from src.rag.models import Base

# Admin engine — connects to postgres DB for user/db management tasks
admin_engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres", isolation_level="AUTOCOMMIT")

try:
    with admin_engine.connect() as conn:
        print("Connected to PostgreSQL as 'postgres'.")

        # Check if user exists before creating
        res = conn.execute(text("SELECT 1 FROM pg_roles WHERE rolname='stock_agent_admin'"))
        if not res.fetchone():
            conn.execute(text("CREATE USER stock_agent_admin WITH PASSWORD '12345678'"))
            print("Created user 'stock_agent_admin'.")
        else:
            print("User 'stock_agent_admin' already exists.")

        # Check if database exists before creating
        res = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='stock_agent'"))
        if not res.fetchone():
            conn.execute(text("CREATE DATABASE stock_agent OWNER stock_agent_admin"))
            print("Created database 'stock_agent'.")
        else:
            print("Database 'stock_agent' already exists.")

except Exception as e:
    print(f"Error occurred: {e}")

# App engine — connects to stock_agent DB to create application tables
app_engine = create_engine("postgresql://postgres:postgres@localhost:5432/stock_agent")

try:
    Base.metadata.create_all(app_engine)
    print("Tables created successfully in 'stock_agent' database.")
except Exception as e:
    print(f"Error creating tables: {e}")
