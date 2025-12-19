"""Main FastAPI application for CamaraPSAP."""

from fastapi import FastAPI
from .device_identifier import router as device_identifier_router
from .location_retrieval import router as location_retrieval_router
from .location_verification import router as location_verification_router
from .oauth import router as oauth_router

app = FastAPI(
    title="CamaraPSAP API",
    description="API for device identification, location retrieval, and location verification with OAuth 2.0 authentication",
    version="0.1.0"
)

# Include routers
app.include_router(oauth_router)  # OAuth endpoints first
app.include_router(device_identifier_router)
app.include_router(location_retrieval_router)
app.include_router(location_verification_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Welcome to CamaraPSAP API",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
