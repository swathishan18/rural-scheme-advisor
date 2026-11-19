"""Rule-based eligibility tool used by the agent.
Rules are simplified for demo purposes - always verify with official sources."""


def check_eligibility(profile: dict):
    """profile keys (any may be missing): age, gender, occupation, annual_income,
    owns_land (bool), has_pucca_house (bool), state, has_girl_child_under_10 (bool)"""
    results = []
    occ = (profile.get("occupation") or "").lower()
    income = profile.get("annual_income")
    gender = (profile.get("gender") or "").lower()
    state = (profile.get("state") or "").lower()

    if profile.get("owns_land") or "farmer" in occ or "vivasayi" in occ:
        results.append(("PM-KISAN", "Farmer family with cultivable land", "Likely"))
    results.append(("MGNREGA", "Any rural adult willing to do unskilled manual work", "Likely"))

    if profile.get("has_pucca_house") is False:
        results.append(("PMAY-G", "Houseless / living in kutcha house", "Likely"))

    results.append(("Ayushman Bharat PM-JAY", "Depends on SECC database / ration card listing", "Check"))

    if profile.get("has_girl_child_under_10"):
        results.append(("Sukanya Samriddhi Yojana", "Girl child below 10 years", "Likely"))

    if gender in ("female", "woman", "women") and "tamil nadu" in state:
        if income is None or income <= 250000:
            results.append(("Magalir Urimai Thogai (TN)", "Woman head of family, income limit", "Check"))
    return results
