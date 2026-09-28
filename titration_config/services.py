from decimal import Decimal

from .models import TitrationLimit


def evaluate_titration_result(
    plant_id,
    titration_type,
    value,
):
    """
    Evaluate a titration result against the active
    limit configured for the selected plant.

    Returns:
        PASS
        FAIL
        REVIEW_REQUIRED
    """

    limit = (
        TitrationLimit.objects
        .filter(
            plant_id=plant_id,
            titration_type=titration_type,
            active=True,
        )
        .first()
    )

    # No active limit configured.
    if limit is None:
        return "REVIEW_REQUIRED"

    value = Decimal(value)

    if (
        value >= limit.min_value
        and value <= limit.max_value
    ):
        return "PASS"

    return "FAIL"