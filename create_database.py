import sqlalchemy
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from dotenv import dotenv_values
import models as m

# connecting environment variables (env)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print(load_dotenv(dotenv_path))

# Database connection
DSN = (f'{dotenv_values()['CONNECTION_DRIVER']}://'
       f'{dotenv_values()['LOGIN']}:'
       f'{dotenv_values()['PASSWORD']}@'
       f'{dotenv_values()['HOST']}:'
       f'{dotenv_values()['PORT']}/'
       f'{dotenv_values()['TITLE_DB']}')

engine = sqlalchemy.create_engine(DSN)
m.create_table(engine)

Session = sessionmaker(bind=engine)
session = Session()


if __name__ == '__main__':

    session.close()
