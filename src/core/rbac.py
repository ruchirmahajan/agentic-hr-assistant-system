"""
Role-Based Access Control (RBAC) system
"""
from enum import Enum
from typing import Set


class Permission(str, Enum):
    """Available permissions in the system"""
    
    # Candidate management
    CANDIDATES_CREATE = "candidates:create"
    CANDIDATES_READ = "candidates:read"
    CANDIDATES_UPDATE = "candidates:update"
    CANDIDATES_DELETE = "candidates:delete"
    CANDIDATES_EXPORT = "candidates:export"
    
    # Job management
    JOBS_CREATE = "jobs:create"
    JOBS_READ = "jobs:read"
    JOBS_UPDATE = "jobs:update"
    JOBS_DELETE = "jobs:delete"
    JOBS_PUBLISH = "jobs:publish"
    
    # Application management
    APPLICATIONS_CREATE = "applications:create"
    APPLICATIONS_READ = "applications:read"
    APPLICATIONS_UPDATE = "applications:update"
    APPLICATIONS_DELETE = "applications:delete"
    APPLICATIONS_PROCESS = "applications:process"
    
    # User management
    USERS_CREATE = "users:create"
    USERS_READ = "users:read"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_MANAGE_ROLES = "users:manage_roles"
    
    # System administration
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_BACKUP = "system:backup"
    
    # Reports and analytics
    REPORTS_VIEW = "reports:view"
    REPORTS_EXPORT = "reports:export"
    ANALYTICS_VIEW = "analytics:view"
    
    # GDPR operations
    GDPR_EXPORT = "gdpr:export"
    GDPR_DELETE = "gdpr:delete"
    GDPR_AUDIT = "gdpr:audit"


# Role permission mappings
ROLE_PERMISSIONS = {
    "admin": {
        # Admin has all permissions
        Permission.CANDIDATES_CREATE,
        Permission.CANDIDATES_READ,
        Permission.CANDIDATES_UPDATE,
        Permission.CANDIDATES_DELETE,
        Permission.CANDIDATES_EXPORT,
        Permission.JOBS_CREATE,
        Permission.JOBS_READ,
        Permission.JOBS_UPDATE,
        Permission.JOBS_DELETE,
        Permission.JOBS_PUBLISH,
        Permission.APPLICATIONS_CREATE,
        Permission.APPLICATIONS_READ,
        Permission.APPLICATIONS_UPDATE,
        Permission.APPLICATIONS_DELETE,
        Permission.APPLICATIONS_PROCESS,
        Permission.USERS_CREATE,
        Permission.USERS_READ,
        Permission.USERS_UPDATE,
        Permission.USERS_DELETE,
        Permission.USERS_MANAGE_ROLES,
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_LOGS,
        Permission.SYSTEM_BACKUP,
        Permission.REPORTS_VIEW,
        Permission.REPORTS_EXPORT,
        Permission.ANALYTICS_VIEW,
        Permission.GDPR_EXPORT,
        Permission.GDPR_DELETE,
        Permission.GDPR_AUDIT,
    },
    
    "hr_manager": {
        # HR Manager has broad access but not system admin
        Permission.CANDIDATES_CREATE,
        Permission.CANDIDATES_READ,
        Permission.CANDIDATES_UPDATE,
        Permission.CANDIDATES_DELETE,
        Permission.CANDIDATES_EXPORT,
        Permission.JOBS_CREATE,
        Permission.JOBS_READ,
        Permission.JOBS_UPDATE,
        Permission.JOBS_DELETE,
        Permission.JOBS_PUBLISH,
        Permission.APPLICATIONS_CREATE,
        Permission.APPLICATIONS_READ,
        Permission.APPLICATIONS_UPDATE,
        Permission.APPLICATIONS_DELETE,
        Permission.APPLICATIONS_PROCESS,
        Permission.USERS_READ,
        Permission.REPORTS_VIEW,
        Permission.REPORTS_EXPORT,
        Permission.ANALYTICS_VIEW,
        Permission.GDPR_EXPORT,
        Permission.GDPR_DELETE,
        Permission.GDPR_AUDIT,
    },
    
    "recruiter": {
        # Recruiters can manage candidates and jobs
        Permission.CANDIDATES_CREATE,
        Permission.CANDIDATES_READ,
        Permission.CANDIDATES_UPDATE,
        Permission.CANDIDATES_EXPORT,
        Permission.JOBS_CREATE,
        Permission.JOBS_READ,
        Permission.JOBS_UPDATE,
        Permission.JOBS_PUBLISH,
        Permission.APPLICATIONS_CREATE,
        Permission.APPLICATIONS_READ,
        Permission.APPLICATIONS_UPDATE,
        Permission.APPLICATIONS_PROCESS,
        Permission.REPORTS_VIEW,
        Permission.ANALYTICS_VIEW,
    },
    
    "interviewer": {
        # Interviewers can view and update applications/candidates
        Permission.CANDIDATES_READ,
        Permission.JOBS_READ,
        Permission.APPLICATIONS_READ,
        Permission.APPLICATIONS_UPDATE,
        Permission.REPORTS_VIEW,
    },
    
    "readonly": {
        # Read-only access
        Permission.CANDIDATES_READ,
        Permission.JOBS_READ,
        Permission.APPLICATIONS_READ,
        Permission.REPORTS_VIEW,
    },
}


def check_permission(user_role: str, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission in ROLE_PERMISSIONS.get(user_role, set())


def get_user_permissions(user_role: str) -> Set[Permission]:
    """Get all permissions for a user role"""
    return ROLE_PERMISSIONS.get(user_role, set())