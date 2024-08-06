from fastapi import APIRouter
from controllers.extractTyc import router as extractTyc_router


GLOBAL_PREFIX = '/api/v1'

# create main router
router = APIRouter()

router.include_router(extractTyc_router, prefix=GLOBAL_PREFIX, tags=["extractTyc"])


