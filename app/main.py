
from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
from .database import engine
from .routers import posts, users, auth, votes
from .config import settings
from fastapi.middleware.cors import CORSMiddleware



# This is going to see if the specified tables are already there, if they are there, 
# it will not do anything, if not, then it will create those tables.

# models.Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = ["https://www.google.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# try: 
#     # conn = psycopg.connect(host='localhost', database='fastapi', user='postgres', password='vendum@99')
#     conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='postgres', cursor_factory=RealDictCursor)
#     cursor = conn.cursor()
#     print("Database connection was successful")
# except Exception as error:
#     print('Database connection failed')
#     print('Error: ', error)


app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)

@app.get("/")
def root():
    return {"message": "hello world"}


