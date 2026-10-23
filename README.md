# Food Support Assistant

A beginner-friendly console pet project for a food-delivery technical support team, using **Python, SQLite, SQL JOIN/SELECT and JSON**. All order data is fictional.

## Requirements
- Python 3.10+ (only standard-library modules are used)

## How to run (Windows / VS Code)
1. Open this folder in VS Code.
2. Open `main.py` and click **Run Python File**, or execute `python main.py` in the integrated terminal.
3. Choose menu actions 1–6 or 0 to exit.

On first run, `support.db` is created, and initial orders are loaded from `orders.json`. Later edits go into SQLite. Use menu option 6 to export the latest orders to `orders_export.json`.

## Demo scenario
1. Choose `1`, then enter `1004`: you should see a cancelled order from Sushi Town.
2. Choose `2`, add `1005` for restaurant `1`.
3. Choose `3`, enter `1005`, choose status `2` (Cooking).
4. Choose `4` to list orders; choose `5` to see totals; choose `6` to export to JSON.
5. Exit and restart the program — changes remain saved in `support.db`.

## SQL covered

Orders and restaurant information are joined via a foreign key:

```sql
SELECT orders.id, restaurants.name, orders.status
FROM orders
JOIN restaurants ON orders.restaurant_id = restaurants.id
WHERE orders.id = '1004';
```

Statistics:

```sql
SELECT status, COUNT(*) FROM orders GROUP BY status;
```

Parameterized queries (`?`) are used for user-provided values.

## Future improvements
- Add unit tests and meaningful logs.
- Add a synthetic service-health check and scheduled execution (cron / Windows Task Scheduler).
- Optional Telegram bot interface.
