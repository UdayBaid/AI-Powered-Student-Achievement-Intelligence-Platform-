
def interpret_grade(predicted_grade: float) -> str:
    if predicted_grade < 10:
        return (
            "The estimated grade is below 10/20. "
            "Review foundational topics and discuss areas of difficulty "
            "with a teacher."
        )

    if predicted_grade < 14:
        return (
            "The estimated grade is between 10 and 14/20. "
            "Consistent revision and targeted practice may help improve "
            "future performance."
        )

    return (
        "The estimated grade is 14/20 or higher. "
        "Continue regular revision and practise challenging questions."
    )
