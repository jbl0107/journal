from fastapi import FastAPI
from routers import user, note

app = FastAPI(title='Journal', version='1.0.0')

# Routers
app.include_router(user.router)
app.include_router(note.router)
