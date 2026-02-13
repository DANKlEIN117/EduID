#!/usr/bin/env python
"""
Simple DB inspector: lists table names and row counts using the Flask app context.
"""
from app import create_app
from app.extensions import db
from sqlalchemy import inspect, text


def inspect_db():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Found {len(tables)} table(s):")
        for t in tables:
            try:
                res = db.session.execute(text(f'SELECT COUNT(*) as cnt FROM "{t}"'))
                cnt = res.scalar()
            except Exception as e:
                cnt = f"error: {e}"
            print(f" - {t}: {cnt}")

if __name__ == '__main__':
    inspect_db()
