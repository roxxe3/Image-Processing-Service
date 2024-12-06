from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JwtBearer(HTTPBearer):
    def __init__(self, auto_Error= True):
        super(JwtBearer, self).__init__(auto_error=auto_Error)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials : HTTPAuthorizationCredentials = await super(JwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme =="Bearer":
                pass