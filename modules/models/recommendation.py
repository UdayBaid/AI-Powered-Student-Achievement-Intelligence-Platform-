
def generate_recommendations(student: dict, predicted_grade: float) -> list[str]:
    recommendations = []
    studytime = student.get("studytime", 2)
    failures = student.get("failures", 0)
    absences = student.get("absences", 0)
    schoolsup = student.get("schoolsup", "no")
    famsup = student.get("famsup", "no")
    if studytime <= 2:
        recommendations.append(
            "Build a consistent weekly study routine. "
            "Set aside focused study sessions and revise lessons regularly."
        )
    else:
        recommendations.append(
            "Maintain your study routine and use practice questions "
            "to check your understanding."
        )
    if failures > 0:
        recommendations.append(
            "Review topics you previously found difficult. "
            "Break them into smaller goals and ask a teacher for help "
            "when concepts remain unclear."
        )
    if absences >= 5:
        recommendations.append(
            "Review lessons missed during absences and make a catch-up "
            "plan. Contact your teacher or classmates for missing notes."
        )
    else:
        recommendations.append(
            "Keep track of missed lessons and revise class notes regularly."
        )
    if schoolsup == "yes":
        recommendations.append(
            "Make use of the school support available to you, "
            "especially for challenging topics."
        )

    if famsup == "yes":
        recommendations.append(
            "Consider setting regular study goals with support from "
            "your family, if that is helpful to you."
        )
    if predicted_grade < 10:
        recommendations.append(
            "Your predicted score is below 10/20. Treat this as an early "
            "signal to review foundational concepts and discuss a study "
            "plan with your teacher."
        )
    elif predicted_grade < 14:
        recommendations.append(
            "Your predicted score is in the middle range. Focus on "
            "weak topics, regular revision, and practice assessments "
            "to work toward improvement."
        )
    else:
        recommendations.append(
            "Your predicted score is in the higher range. Continue "
            "revising consistently and practise more challenging questions."
        )

    return recommendations
