from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from models.base import Base
from models.user import User
from models.note import Note

from urllib.parse import quote_plus

from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv('DB_USER_J')
DB_PASSWORD = quote_plus(os.getenv('DB_PASSWORD_J')) # escapa caracteres especiales
DB_HOST = os.getenv('DB_HOST_J')
DB_PORT = os.getenv('DB_PORT_J')
DB_NAME = os.getenv('DB_NAME_J')


engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

SessionLocal = sessionmaker(bind=engine)

def get_db():
    with SessionLocal() as session:
        yield session


def main():
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)
    # insertSampleData() 
    # deleteSampleData()

    pass

#Datos de prueba
def insertSampleData():
    with SessionLocal() as session:
        with session.begin():
            users = [
                User(first_name="squidward", last_name="Tentacles", username='squidtent', age=22, password='12345678'),
                User(first_name="Eugene", last_name="H. Krabs", username='ehkrabs', age=20, password='12345678'),
                User(first_name="Pepe", last_name="Ruiz", username='ejemplo', age=24, email='correo@hotmail.com', password='12345678')
            ] 
            

            users[0].notes.append(Note(title='Nota 1', description='Esta es una descripcion de ejemplo'))
            users[0].notes.append(Note(title='Nota 2', description='Probando 2 notas en un mismo usuario'))
            users[1].notes.append(Note(title='Ultima nota', description='Nueva nota en nuevo user'))


            session.add_all(users)
           

def deleteSampleData():
    with SessionLocal() as session:
        with session.begin():
            # Este delete se salta el ORM. Funciona gracias a ondelete='CASCADE' en Note (si no daria error de integridad ref)
            # passive_deletes=True mejora eficiencia si se borrara desde el ORM, evitando cargar los hijos
            # (tiene q definirse el oncascade si o si en este caso)
            session.execute(delete(User))




if __name__ == '__main__':
    main()