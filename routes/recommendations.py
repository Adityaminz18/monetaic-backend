from fastapi import APIRouter

router = APIRouter()

@router.get("/recommendations/bad-habits")
async def list_bad_habits():
    return {
        "bad_habits": [
            "Overspending on non-essentials",
            "Not tracking expenses",
            "Ignoring debt repayment"
        ]
    }

@router.get("/recommendations/good-practices")
async def list_good_practices():
    return {
        "good_practices": [
            "Create a monthly budget",
            "Save at least 20% of your income",
            "Invest in diversified assets"
        ]
    }