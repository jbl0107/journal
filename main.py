from fastapi import FastAPI
from routers import user

app = FastAPI(title='Journal', version='1.0.0')

# Routers
app.include_router(user.router)
