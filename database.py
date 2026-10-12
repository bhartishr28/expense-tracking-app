
import os
import psycopg2
import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

load_dotenv()


def get_setting(name):
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except StreamlitSecretNotFoundError:
        pass

    return os.getenv(name)


def get_connection():
    config = {
        "DB_HOST": get_setting("DB_HOST"),
        "DB_PORT": get_setting("DB_PORT"),
        "DB_NAME": get_setting("DB_NAME"),
        "DB_USER": get_setting("DB_USER"),
        "DB_PASSWORD": get_setting("DB_PASSWORD"),
    }

    missing = [
        name for name, value in config.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing database settings: " + ", ".join(missing)
        )

    return psycopg2.connect(
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        database=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
    )
def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        select * from categories order by id asc;
        ''')
        categories = cursor.fetchall()
        return categories

    finally:
        cursor.close()
        conn.close()

def get_payment_methods():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        select * from payment_methods order by id asc;
        ''')
        payment_methods = cursor.fetchall()
        return payment_methods

    finally:
        cursor.close()
        conn.close()

def add_expenses(expense_date, category_id, description, amount, payment_method_id, notes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = '''
        insert into expenses (expense_date, category_id, description, amount, payment_method_id, notes) values (%s, %s, %s, %s, %s, %s)
        returning id;
        '''

        data = (expense_date, category_id, description, amount, payment_method_id, notes)
        cursor.execute(query, data)
        expense_id = cursor.fetchone()[0]
        conn.commit()

        return expense_id
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_expenses():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = ''' select e.id,e.expense_date,c.name as category,e.description,e.amount
         ,pm.name as payment_method,e.notes
         from expenses e 
        join categories c on e.category_id = c.id
        join payment_methods pm on e.payment_method_id = pm.id
        order by e.id desc, e.expense_date desc
        '''
        cursor.execute(query)
        expenses = cursor.fetchall()
        return expenses
    finally:
        cursor.close()
        conn.close()

def update_expenses(expense_id,expense_date, category_id, description, amount, payment_method_id, notes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = '''
        update expenses 
        set expense_date = %s, category_id = %s, description = %s, amount = %s, payment_method_id = %s, notes = %s
        where id = %s'''

        data = (expense_date, category_id, description, amount, payment_method_id, notes,expense_id)
        cursor.execute(query, data)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.commit()

        cursor.close()
        conn.close()

def delete_expenses(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = '''
        delete from expenses 
        where id = %s'''

        data = (expense_id,)
        cursor.execute(query, data)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.commit()
        cursor.close()
        conn.close()
