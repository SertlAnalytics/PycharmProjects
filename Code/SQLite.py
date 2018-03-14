import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from sqlalchemy import func

conn = sqlite3.connect('MyFirstdb.db')

c = conn.cursor()

c.execute("""Create table Employee(
            firstName text,
            lastName text,
            salary integer
          )""")

conn.commit()
conn.close()
