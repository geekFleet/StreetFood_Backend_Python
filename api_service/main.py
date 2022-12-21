from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
import models
from utils.dbUtil import SessionLocal, engine
from users import router as user_router
from opts import router as otp_router
from vendor import router as vendor_router
from review import router as review_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # FastAPI doc related to allow_origin (to avoid CORS issues):
    # "It's also possible to declare the list as "*" (a "wildcard") to say that all are allowed.
    # But that will only allow certain types of communication, excluding everything that involves
    # credentials: Cookies, Authorization headers like those used with Bearer Tokens, etc.
    # So, for everything to work correctly, it's better to specify explicitly the allowed origins."
    # => Workarround: use allow_origin_regex
    # Source: https://github.com/tiangolo/fastapi/issues/133#issuecomment-646985050
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def index():
    return "hello"


app.include_router(auth_router.router, tags=["Auth"])
app.include_router(user_router.router, tags=["User"])
app.include_router(otp_router.router, tags=["OTP"])
app.include_router(vendor_router.router, tags=["Vendor"])
app.include_router(review_router.router, tags=["Review"])
