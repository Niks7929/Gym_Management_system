from typing import List, Optional
from ninja import Router
from ninja.errors import HttpError
from .models import Branch, GymSetting
from .schemas import BranchOut, BranchCreate, BranchUpdate, GymSettingOut, GymSettingUpdate
from apps.accounts.auth import jwt_auth, require_roles
from apps.accounts.models import UserRole

router = Router(tags=["Branches & Settings"])

# Public endpoint: Allow anyone to view active branches
@router.get("/branches", response=List[BranchOut], auth=None)
def list_branches(request, is_active: Optional[bool] = None):
    qs = Branch.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return list(qs.order_by('name'))

@router.post("/branches", response={201: BranchOut}, auth=jwt_auth)
def create_branch(request, payload: BranchCreate):
    require_roles(UserRole.ADMIN)(request.auth)
    
    if Branch.objects.filter(code=payload.code).exists():
        raise HttpError(400, "Branch code must be unique")
        
    branch = Branch.objects.create(
        name=payload.name,
        code=payload.code,
        address=payload.address,
        city=payload.city,
        phone=payload.phone,
        email=payload.email or ""
    )
    return 201, branch

@router.get("/branches/{branch_id}", response=BranchOut, auth=None)
def get_branch(request, branch_id: int):
    branch = Branch.objects.filter(id=branch_id).first()
    if not branch:
        raise HttpError(404, "Branch not found")
    return branch

@router.put("/branches/{branch_id}", response=BranchOut, auth=jwt_auth)
def update_branch(request, branch_id: int, payload: BranchUpdate):
    require_roles(UserRole.ADMIN)(request.auth)
    branch = Branch.objects.filter(id=branch_id).first()
    if not branch:
        raise HttpError(404, "Branch not found")

    if payload.name is not None:
        branch.name = payload.name
    if payload.code is not None:
        if Branch.objects.filter(code=payload.code).exclude(id=branch_id).exists():
            raise HttpError(400, "Branch code already exists")
        branch.code = payload.code
    if payload.address is not None:
        branch.address = payload.address
    if payload.city is not None:
        branch.city = payload.city
    if payload.phone is not None:
        branch.phone = payload.phone
    if payload.email is not None:
        branch.email = payload.email
    if payload.is_active is not None:
        branch.is_active = payload.is_active

    branch.save()
    return branch

@router.delete("/branches/{branch_id}", response={200: dict}, auth=jwt_auth)
def delete_branch(request, branch_id: int):
    require_roles(UserRole.ADMIN)(request.auth)
    branch = Branch.objects.filter(id=branch_id).first()
    if not branch:
        raise HttpError(404, "Branch not found")
    branch.is_active = False
    branch.save()
    return 200, {"message": f"Branch {branch.name} deactivated"}

# Public endpoint: Allow anyone to view settings for Home and UI
@router.get("/settings", response=GymSettingOut, auth=None)
def get_settings(request):
    setting = GymSetting.objects.first()
    if not setting:
        setting = GymSetting.objects.create()
    return setting

# Admin only: Update CMS and settings
@router.put("/settings", response=GymSettingOut, auth=jwt_auth)
def update_settings(request, payload: GymSettingUpdate):
    require_roles(UserRole.ADMIN)(request.auth)
    setting = GymSetting.objects.first()
    if not setting:
        setting = GymSetting.objects.create()

    for field, value in payload.dict(exclude_unset=True).items():
        if value is not None:
            setattr(setting, field, value)

    setting.save()
    return setting
