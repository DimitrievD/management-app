# services/notification-service/main.py
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
import time # For simulating work

app = FastAPI(
    title="Notification Service",
    description="Handles sending notifications like emails or in-app messages.",
    version="0.1.0"
)

# --- Models ---
class NotificationPayload(BaseModel):
    recipient: EmailStr | str # Could be email or user ID for in-app
    subject: str
    message: str
    type: str = "email" # e.g., 'email', 'in-app', 'sms'

# --- Helper Function (Simulated) ---
def send_email_notification(payload: NotificationPayload):
    # In a real app, integrate with an email service (SMTP, SendGrid, Mailgun, etc.)
    print(f"Simulating sending {payload.type} notification...")
    print(f"To: {payload.recipient}")
    print(f"Subject: {payload.subject}")
    print(f"Message: {payload.message}")
    time.sleep(2) # Simulate network latency/work
    print("Notification 'sent'.")

# --- API Endpoint ---
@app.post("/send-notification", status_code=status.HTTP_202_ACCEPTED)
async def send_notification_endpoint(
    payload: NotificationPayload,
    background_tasks: BackgroundTasks # Use background tasks for non-critical operations
):
    """
    Accepts a notification request and schedules it for sending.
    Uses background tasks so the API call returns quickly.
    """
    print(f"Received notification request for {payload.recipient}")

    # Schedule the actual sending as a background task
    # This allows the API to respond quickly without waiting for the email to send
    background_tasks.add_task(send_email_notification, payload)

    return {"message": "Notification request accepted and scheduled for sending."}

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}

# --- How will this be triggered? ---
# Option 1: Direct REST call from Task Service (or others)
#   - Task Service makes a POST request to /send-notification here.
#   - Simpler setup, but creates coupling.
# Option 2: Message Queue (e.g., RabbitMQ, Kafka) - Preferred for Microservices
#   - Task Service publishes a "notification_request" event/message to a queue.
#   - Notification Service subscribes to that queue and processes messages.
#   - More resilient, decoupled, better for handling load spikes.
# We'll start with the idea of a direct REST call conceptually,
# but design towards potentially adding a message queue later.