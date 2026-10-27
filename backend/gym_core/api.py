from ninja import NinjaAPI
from ninja.errors import HttpError
from apps.accounts.routers import router as accounts_router
from apps.branches.routers import router as branches_router
from apps.memberships.routers import router as memberships_router
from apps.attendance.routers import router as attendance_router
from apps.training.routers import router as training_router
from apps.analytics.routers import router as analytics_router

api = NinjaAPI(
    title="SETFIT Gym Management System API",
    version="2.0.0",
    description="Enterprise-grade Gym Management REST API with RBAC (Admin, Receptionist, Trainer, Member)",
    docs_url="/docs"
)

# Custom exception handler for clean error responses
@api.exception_handler(HttpError)
def on_http_error(request, exc):
    return api.create_response(
        request,
        {"detail": exc.message, "status_code": exc.status_code},
        status=exc.status_code
    )

# Register routers
api.add_router("/auth", accounts_router)
api.add_router("/", branches_router)
api.add_router("/", memberships_router)
api.add_router("/", attendance_router)
api.add_router("/", training_router)
api.add_router("/analytics", analytics_router)
