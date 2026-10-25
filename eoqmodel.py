"""Cost calculations for individual artwork instances."""

from math import isfinite


def calculate_total_artwork_cost(
    frame_costs,
    canvas_costs,
    paint_costs,
    brush_costs,
    hourly_rates,
    hours_worked,
    storage_rent,
):
    """Calculate costs for parallel arrays of artwork instances.

    Each index represents one artwork. Storage rent is included once in the
    grand total, not once per artwork.
    """
    arrays = {
        "frame_costs": frame_costs,
        "canvas_costs": canvas_costs,
        "paint_costs": paint_costs,
        "brush_costs": brush_costs,
        "hourly_rates": hourly_rates,
        "hours_worked": hours_worked,
    }

    normalized = {}
    for name, values in arrays.items():
        if isinstance(values, (str, bytes)):
            raise TypeError(f"{name} must be an array of numeric values")
        try:
            normalized[name] = list(values)
        except TypeError as exc:
            raise TypeError(f"{name} must be an array of numeric values") from exc

    instance_count = len(normalized["frame_costs"])
    for name, values in normalized.items():
        if len(values) != instance_count:
            raise ValueError(
                f"{name} must contain {instance_count} values to match frame_costs"
            )

    try:
        rent = float(storage_rent)
    except (TypeError, ValueError) as exc:
        raise TypeError("storage_rent must be numeric") from exc

    for name, values in normalized.items():
        for index, value in enumerate(values):
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise TypeError(f"{name}[{index}] must be numeric") from exc
            if not isfinite(number):
                raise ValueError(f"{name}[{index}] must be finite")
            if number < 0:
                raise ValueError(f"{name}[{index}] cannot be negative")
            values[index] = number

    if not isfinite(rent):
        raise ValueError("storage_rent must be finite")
    if rent < 0:
        raise ValueError("storage_rent cannot be negative")

    frame_cost = sum(normalized["frame_costs"])
    canvas_cost = sum(normalized["canvas_costs"])
    paint_cost = sum(normalized["paint_costs"])
    brush_cost = sum(normalized["brush_costs"])

    allocated_rent = rent / instance_count if instance_count else 0.0
    instance_totals = [
        frame + canvas + paint + brush + (rate * hours) + allocated_rent
        for frame, canvas, paint, brush, rate, hours in zip(
            normalized["frame_costs"],
            normalized["canvas_costs"],
            normalized["paint_costs"],
            normalized["brush_costs"],
            normalized["hourly_rates"],
            normalized["hours_worked"],
        )
    ]
    selling_prices = [cost * 1.70 for cost in instance_totals]

    labor_cost = sum(
        rate * hours
        for rate, hours in zip(
            normalized["hourly_rates"], normalized["hours_worked"]
        )
    )
    total_cost = frame_cost + canvas_cost + paint_cost + brush_cost + labor_cost + rent

    return {
        "frame_cost": frame_cost,
        "canvas_cost": canvas_cost,
        "paint_cost": paint_cost,
        "brush_cost": brush_cost,
        "labor_cost": labor_cost,
        "storage_rent": rent,
        "allocated_rent_per_artwork": allocated_rent,
        "instance_totals": instance_totals,
        "suggested_selling_prices": selling_prices,
        "markup_percentage": 70.0,
        "total_cost": total_cost,
    }


def calculate_total_cost(*args, **kwargs):
    """Short alias for calculate_total_artwork_cost."""
    return calculate_total_artwork_cost(*args, **kwargs)


