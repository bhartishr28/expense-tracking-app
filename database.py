import os
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_connection():

    if "DB_HOST" in st.secrets:
        return psycopg2.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            database=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"]
        )

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
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
