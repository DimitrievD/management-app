from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer # Or OpenIdConnect for discovery
from jose import jwt, JWTError
from pydantic import BaseModel
import requests # To fetch Keycloak public key

# --- Keycloak Configuration ---
KEYCLOAK_URL = "http://localhost:8080" # Use Docker service name 'keycloak' later
REALM_NAME = "task-app-realm"
# In a real app, these would come from env vars or config service
KEYCLOAK_PUBLIC_KEY = None

# --- FastAPI App ---
app = FastAPI()

# --- Fetch Keycloak Public Key ---
def get_keycloak_public_key():
    global KEYCLOAK_PUBLIC_KEY
    if KEYCLOAK_PUBLIC_KEY is None:
        try:
            # Construct the certs URL dynamically
            certs_url = f"{KEYCLOAK_URL}/auth/realms/{REALM_NAME}/protocol/openid-connect/certs"
            response = requests.get(certs_url)
            response.raise_for_status() # Raise an exception for bad status codes
            jwks = response.json()

            # Find the RSA signing key (usually 'sig' use)
            rsa_key = next((key for key in jwks['keys'] if key['use'] == 'sig' and key['kty'] == 'RSA'), None)

            if rsa_key:
                # Construct the public key in PEM format
                KEYCLOAK_PUBLIC_KEY = (
                    "-----BEGIN PUBLIC KEY-----\n"
                    f"{rsa_key['x5c'][0]}" # Usually the first cert in the chain
                    "\n-----END PUBLIC KEY-----"
                )
                print("Successfully fetched Keycloak public key.")
            else:
                 print("Error: RSA signing key not found in JWKS.")
                 raise HTTPException(status_code=500, detail="Could not fetch Keycloak public key")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Keycloak public key: {e}")
            # Handle error appropriately, maybe retry or exit
            raise HTTPException(status_code=500, detail="Could not fetch Keycloak public key")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="Error processing Keycloak public key")
    return KEYCLOAK_PUBLIC_KEY


# --- Authentication Dependency ---
# This expects the token in the Authorization header: Bearer <token>
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_URL}/auth/realms/{REALM_NAME}/protocol/openid-connect/auth", # Not directly used by API, but good practice
    tokenUrl=f"{KEYCLOAK_URL}/auth/realms/{REALM_NAME}/protocol/openid-connect/token" # Not directly used by API
)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    public_key = get_keycloak_public_key()
    if not public_key:
         raise HTTPException(status_code=500, detail="Authentication service not properly configured")

    try:
        # Decode the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"], # Algorithm used by Keycloak
            # Specify audience if your clients have it configured
            # audience="account", # Default Keycloak audience, adjust if needed for your client
            options={"verify_aud": False} # Set to True and add audience if needed
        )
        username: str = payload.get("preferred_username")
        user_id: str = payload.get("sub") # Keycloak User ID
        roles: list = payload.get("realm_access", {}).get("roles", [])

        if username is None or user_id is None:
            raise credentials_exception
        # You can return a user model here
        return {"username": username, "id": user_id, "roles": roles }
    except JWTError as e:
        print(f"JWT Error: {e}") # Log the error
        raise credentials_exception
    except Exception as e:
        print(f"Token validation error: {e}") # Log unexpected errors
        raise credentials_exception

# --- Pydantic Models (Data Shapes) ---
class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str = "todo"
    assignee_id: str | None = None # Link to Keycloak user ID

# Dummy database for now
fake_db = {
    1: Task(id=1, title="Setup Keycloak", description="Run Keycloak via Docker", status="done"),
    2: Task(id=2, title="Create Task Service", description="Build basic FastAPI app", status="inprogress"),
}

# --- API Endpoints ---
@app.on_event("startup")
async def startup_event():
    print("Fetching Keycloak public key on startup...")
    get_keycloak_public_key() # Fetch key on startup

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Task Management Service"}

# Example protected endpoint
@app.get("/tasks/", response_model=list[Task])
async def get_tasks(current_user: dict = Depends(get_current_user)):
     # Later: Filter tasks based on current_user roles or assignments
    print(f"User {current_user['username']} requested tasks.")
    return list(fake_db.values())

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int, current_user: dict = Depends(get_current_user)):
    if task_id not in fake_db:
         raise HTTPException(status_code=404, detail="Task not found")
    # Later: Add authorization checks (can this user view this task?)
    print(f"User {current_user['username']} requested task {task_id}.")
    return fake_db[task_id]

@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: Task, current_user: dict = Depends(get_current_user)):
    # Basic role check example
    if "project_manager" not in current_user['roles'] and "app_admin" not in current_user['roles']:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to create tasks")

    new_id = max(fake_db.keys()) + 1 if fake_db else 1
    new_task = task_data.copy(update={"id": new_id})
    fake_db[new_id] = new_task
    print(f"User {current_user['username']} created task {new_id}.")
    return new_task

# Add PUT, DELETE endpoints similarly, with auth checks

# Endpoint to check user info from token (for debugging)
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user