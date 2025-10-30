"""
Schemas Pydantic da aplicação
"""

from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserChangePassword, 
    UserResponse, UserProfile, UserStats
)
from app.schemas.auth import (
    LoginRequest, LoginResponse, TokenData, 
    PasswordResetRequest, PasswordResetConfirm,
    RefreshTokenRequest, ApiKeyResponse
)
from app.schemas.account import (
    AccountBase, AccountCreate, AccountUpdate, AccountResponse,
    AccountSummary, AccountBalance, AccountStats
)
from app.schemas.category import (
    CategoryBase, CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryTree, CategorySummary, CategoryStats, CategoryBudgetSummary
)
from app.schemas.transaction import (
    TransactionBase, TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionWithDetails, TransactionSummary, TransactionImport,
    TransactionImportResult, TransactionBulkUpdate, TransactionFilter
)
from app.schemas.budget import (
    BudgetBase, BudgetCreate, BudgetUpdate, BudgetResponse,
    BudgetWithCategory, BudgetSummary, BudgetStats,
    BudgetAnalysis, BudgetFilter, BudgetCopy
)
from app.schemas.recurring_rule import (
    RecurringRuleBase, RecurringRuleCreate, RecurringRuleUpdate,
    RecurringRuleResponse, RecurringRuleWithDetails, RecurringRuleSummary,
    RecurringRuleExecution, RecurringRuleRunRequest, RecurringRuleRunResult,
    RecurringRuleFilter
)
from app.schemas.dashboard import (
    DashboardSummary,
    MonthlyFlow,
    CategorySummary,
    UpcomingExpense,
    BudgetStatusItem,
    BudgetStatusSummary,
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserChangePassword",
    "UserResponse", "UserProfile", "UserStats",
    
    # Auth
    "LoginRequest", "LoginResponse", "TokenData",
    "PasswordResetRequest", "PasswordResetConfirm",
    "RefreshTokenRequest", "ApiKeyResponse",
    
    # Account
    "AccountBase", "AccountCreate", "AccountUpdate", "AccountResponse",
    "AccountSummary", "AccountBalance", "AccountStats",
    
    # Category
    "CategoryBase", "CategoryCreate", "CategoryUpdate", "CategoryResponse",
    "CategoryTree", "CategorySummary", "CategoryStats", "CategoryBudgetSummary",
    
    # Transaction
    "TransactionBase", "TransactionCreate", "TransactionUpdate", "TransactionResponse",
    "TransactionWithDetails", "TransactionSummary", "TransactionImport",
    "TransactionImportResult", "TransactionBulkUpdate", "TransactionFilter",
    
    # Budget
    "BudgetBase", "BudgetCreate", "BudgetUpdate", "BudgetResponse",
    "BudgetWithCategory", "BudgetSummary", "BudgetStats",
    "BudgetAnalysis", "BudgetFilter", "BudgetCopy",
    
    # Recurring Rule
    "RecurringRuleBase", "RecurringRuleCreate", "RecurringRuleUpdate",
    "RecurringRuleResponse", "RecurringRuleWithDetails", "RecurringRuleSummary",
    "RecurringRuleExecution", "RecurringRuleRunRequest", "RecurringRuleRunResult",
    "RecurringRuleFilter",
    
    # Dashboard
    "DashboardSummary",
    "MonthlyFlow",
    "CategorySummary",
    "UpcomingExpense",
    "BudgetStatusItem",
    "BudgetStatusSummary",
]
