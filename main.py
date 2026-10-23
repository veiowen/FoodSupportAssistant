"""Food Support Assistant — a small CLI for demo food-delivery orders."""
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "support.db"
JSON_PATH = BASE_DIR / "orders.json"
STATUSES = ("Created", "Cooking", "On the way", "Delivered", "Cancelled")


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def setup_database(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY, restaurant_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
    )""")
    connection.executemany(
        "INSERT OR IGNORE INTO restaurants (id, name) VALUES (?, ?)",
        [(1, "Pizza House"), (2, "Sushi Town")]
    )
    count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    if count == 0 and JSON_PATH.exists():
        with JSON_PATH.open("r", encoding="utf-8") as file:
            initial_orders = json.load(file)
        for order in initial_orders:
            connection.execute(
                "INSERT INTO orders (id, restaurant_id, status) VALUES (?, ?, ?)",
                (str(order["id"]), order["restaurant_id"], order["status"])
            )
    connection.commit()


def find_order(connection):
    order_id = input("Enter order ID: ").strip()
    row = connection.execute("""SELECT orders.id, restaurants.name, orders.status
        FROM orders JOIN restaurants ON orders.restaurant_id = restaurants.id
        WHERE orders.id = ?""", (order_id,)).fetchone()
    if row:
        print(f"Order: {row[0]} | Restaurant: {row[1]} | Status: {row[2]}")
    else:
        print("Order not found!")


def add_order(connection):
    order_id = input("New order ID: ").strip()
    if not order_id.isdigit():
        print("Order ID must contain digits only.")
        return
    print("Restaurants: 1 - Pizza House, 2 - Sushi Town")
    restaurant_id = input("Restaurant ID: ").strip()
    if restaurant_id not in ("1", "2"):
        print("Unknown restaurant.")
        return
    try:
        with connection:
            connection.execute("INSERT INTO orders VALUES (?, ?, ?)",
                               (order_id, int(restaurant_id), "Created"))
        print("Order created!")
    except sqlite3.IntegrityError:
        print("This order ID already exists!")


def update_order(connection):
    order_id = input("Order ID to update: ").strip()
    row = connection.execute("SELECT status FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        print("Order not found!")
        return
    for index, status in enumerate(STATUSES, 1):
        print(f"{index}. {status}")
    choice = input("Choose new status (1-5): ").strip()
    if choice not in ("1", "2", "3", "4", "5"):
        print("Invalid status number.")
        return
    with connection:
        connection.execute("UPDATE orders SET status = ? WHERE id = ?",
                           (STATUSES[int(choice) - 1], order_id))
    print("Status updated!")


def show_orders(connection):
    rows = connection.execute("""SELECT orders.id, restaurants.name, orders.status
        FROM orders JOIN restaurants ON orders.restaurant_id = restaurants.id
        ORDER BY orders.id""").fetchall()
    for order_id, restaurant, status in rows:
        print(f"{order_id} | {restaurant} | {status}")
    if not rows:
        print("No orders yet.")


def show_statistics(connection):
    rows = connection.execute("""SELECT status, COUNT(*)
        FROM orders GROUP BY status ORDER BY status""").fetchall()
    for status, count in rows:
        print(f"{status}: {count}")


def export_json(connection):
    rows = connection.execute(
        "SELECT id, restaurant_id, status FROM orders ORDER BY id"
    ).fetchall()
    data = [{"id": item[0], "restaurant_id": item[1], "status": item[2]}
            for item in rows]
    export_path = BASE_DIR / "orders_export.json"
    with export_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"Exported {len(data)} orders to {export_path.name}")


def main():
    try:
        with connect() as connection:
            setup_database(connection)
            actions = {"1": find_order, "2": add_order, "3": update_order,
                       "4": show_orders, "5": show_statistics, "6": export_json}
            while True:
                print("\n=== FOOD SUPPORT ASSISTANT ===")
                print("1. Find an order\n2. Add a new order\n3. Update order status")
                print("4. View all orders\n5. View statistics\n6. Export JSON\n0. Exit")
                choice = input("Choose an option: ").strip()
                if choice == "0":
                    print("Goodbye!")
                    break
                action = actions.get(choice)
                if action:
                    action(connection)
                else:
                    print("Invalid option. Try again.")
    except (OSError, json.JSONDecodeError, sqlite3.Error) as error:
        print(f"Unable to start or use project data: {error}")


if __name__ == "__main__":
    main()
