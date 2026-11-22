# main.py - Điểm khởi chạy FastAPI, CORS và đăng ký router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='SpaceX HRM Distributed API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def root():
    return {'message': 'SpaceX HRM Distributed Backend is running'}
