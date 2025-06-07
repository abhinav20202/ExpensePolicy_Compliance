from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# ✅ Grouped Routers
from app.routers.ingestion import router as ingestion_router
from app.routers.compliance import router as compliance_router
app = FastAPI(
   title="ExpensePolicy Auditor",
   description="A GenAI system for receipt validation and policy compliance.",
   version="1.0.0"
)

import logging
import traceback
from fastapi.responses import JSONResponse
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
   tb = traceback.format_exc()
   logging.error(f"Unhandled Exception: {tb}")
   return JSONResponse(
       status_code=500,
       content={"detail": f"Internal Server Error: {str(exc)}"},
   )

# 🔗 CORS Middleware (open in dev)
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)
# ✅ Register Route Groups
app.include_router(ingestion_router, prefix="/ingest", tags=["Ingestion"])
app.include_router(compliance_router, prefix="/compliance", tags=["Compliance Check"])
# ▶️ Entry Point
if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)