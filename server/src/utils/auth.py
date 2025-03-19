from typing import Optional
from fastapi import Request, HTTPException
import jwt
from pydantic import BaseModel

class TokenPayload(BaseModel):
    tenant_id: str
    user_id: str

class AuthContext(BaseModel):
    tenant_id: str
    user_id: str

async def get_auth_context(request: Request) -> AuthContext:
    token = request.headers.get("Authorization")
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization token"
        )
    
    if not token.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )
    
    try:
        # Remove 'Bearer ' prefix
        token = token.split(" ")[1]
        # You should get this from environment variables
        secret_key = "your-secret-key"  # TODO: Move to environment variables
        
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
        
        return AuthContext(
            tenant_id=token_data.tenant_id,
            user_id=token_data.user_id
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication error: {str(e)}"
        )