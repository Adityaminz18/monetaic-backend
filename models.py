from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List, Literal, Dict, Any

class EMI(BaseModel):
    name: str
    amount: float  # ✅ Changed from str to float
    interest: float  # ✅ Changed from str to float

class ExtraCost(BaseModel):
    name: str
    amount: float  # ✅ Changed from str to float

class MonthlyFixedExpenses(BaseModel):
    housing: float  # ✅ Changed from str to float
    utilities: float
    transportation: float
    food: float

class MonthlyVariableExpenses(BaseModel):
    entertainment: float
    personal: float

class MonthlyExpenses(BaseModel):
    fixed: MonthlyFixedExpenses
    variable: MonthlyVariableExpenses

class FinancialGoals(BaseModel):
    LongTermGoals: List[str]
    ShortTermGoal: List[str] = []  # ✅ Changed from "" to List[str]

class FinancialData(BaseModel):
    monthlyIncome: float  # ✅ Changed from str to float
    savingsGoal: float  # ✅ Changed from str to float
    investmentTimeframe: constr(strip_whitespace=True)
    riskTolerance: Literal["conservative", "moderate", "aggressive"]
    expenses: MonthlyExpenses
    financial_goals: FinancialGoals
    savings: float = 0
    debts: Optional[float] = 0.0
    investments: Optional[float] = 0.0
    emis: List[EMI] = []
    extraCosts: List[ExtraCost] = []

class User(BaseModel):
    email: EmailStr
    fullName: str
    age: int  # ✅ Changed from str to int
    occupation: str

class PostUserDetail(User):
    financial: FinancialData

class RequestEmail(BaseModel):
    email: EmailStr

class UserInDB(PostUserDetail):
    longterm: Dict[str, Any] = {}  
    shortterm: Dict[str, Any] = {}  
    spend_analysis: Dict[str, Any] = {}  
    bad_habits: Dict[str, Any] = {}  # ✅ New Field: Stores user's bad financial habits
    good_habits: Dict[str, Any] = {}  # ✅ New Field: Stores user's good financial habits
    insights: Dict[str, Any] = {}  # ✅ New Field: Stores general financial insights