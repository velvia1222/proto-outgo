import sqlite3

con = sqlite3.connect('outgo_db.sqlite')
cursor = con.cursor()
cursor.execute('''drop table if exists outgo;''')
cursor.execute('''
        create table outgo (
            number integer primary key,
            status text,
            buyer text,
            amount integer not null,
            category);
''')
con.commit()