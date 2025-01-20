from src.routes.credit_types import router as credit_types_router
from src.routes.insights import router as insights_router
from src.routes.products import router as products_router
from src.routes.transactions import router as transactions_router
from src.routes.wallets import router as wallets_router
from src.utils.router import APIRouter

router = APIRouter()

router.include_router(wallets_router)
router.include_router(credit_types_router)
router.include_router(insights_router)
router.include_router(transactions_router)
router.include_router(products_router)
