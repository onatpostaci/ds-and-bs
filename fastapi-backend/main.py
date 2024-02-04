from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ripple

app = FastAPI()

# Set up CORS middleware
origins = [
    "http://localhost:3000", # Add the URL of your frontend application
    # You can add more origins as needed, or use ["*"] to allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # List of allowed methods
    allow_headers=["*"],  # List of allowed headers
)

app.include_router(ripple.router)


# Optional: Run the application using Uvicorn for development purposes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)