import hashlib
import uuid
from datetime import datetime

import psycopg2
from core.config import settings

SUPERUSER = 'superuser'

if __name__ == '__main__':
    print('Enter login:')
    username = input()
    print('Enter password:')
    password = input()
    salt = username.encode('utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

    conn = psycopg2.connect(database=settings.postgres_db,
                            user=settings.postgres_user,
                            password=settings.postgres_password,
                            host=settings.postgres_host,
                            port=settings.postgres_port)
    cur = conn.cursor()
    user_id = uuid.uuid4()
    cur.execute('insert into users (id, email, hashed_password, created) values (%s, %s, %s, %s)',
                (str(user_id), username, hashed_password, datetime.now()))
    cur.execute(f"select id from roles where name = '{SUPERUSER}'")
    role_id = cur.fetchone()
    if role_id:
        cur.execute('insert into user_role values(%s, %s)', (str(user_id), role_id))
        message = f'added superuser with id = {user_id}'
    else:
        role_id = uuid.uuid4()
        cur.execute('insert into roles values(%s, %s, %s)', (str(role_id), SUPERUSER, datetime.now()))
        message = f'added role superuser with id = {role_id}\n'
        cur.execute('insert into user_role values(%s, %s)', (str(user_id), str(role_id)))
        message += f'added superuser with id = {user_id}'
    conn.commit()
    print(message)
