from fastapi import FastAPI

from app.api.customers import router as customer_router
from app.api.loans import router as loan_router
from app.api.tickets import router as ticket_router
from app.api.chat import router as chat_router

app = FastAPI(
    title="Loanfront AI Customer Support",
    version="0.1.0",
)

app.include_router(customer_router)
app.include_router(loan_router)
app.include_router(ticket_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}