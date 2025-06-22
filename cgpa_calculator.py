def calculate_required_marks(current_cgpa, credits_completed, credits_remaining, target_cgpa, grading_scale='cgpa'):
    """
    Calculate required marks or CGPA points for remaining courses.
    
    Args:
        current_cgpa (float): Current CGPA (0-10) or percentage (0-100%).
        credits_completed (int): Total credits completed (non-negative).
        credits_remaining (int): Total credits remaining (non-negative).
        target_cgpa (float): Target CGPA (0-10) or percentage (0-100%).
        grading_scale (str): 'cgpa' (10-point) or 'percentage' (0-100%).
    
    Returns:
        float or None: Required average for remaining courses, or None if no credits remain.
    
    Raises:
        ValueError: If inputs are invalid (e.g., negative credits, invalid CGPA/percentage).
    """
    # Input validation
    if grading_scale not in ['cgpa', 'percentage']:
        raise ValueError("grading_scale must be 'cgpa' or 'percentage'")
    
    max_value = 10.0 if grading_scale == 'cgpa' else 100.0
    if not (0 <= current_cgpa <= max_value):
        raise ValueError(f"Current {grading_scale} must be between 0 and {max_value}")
    if not (0 <= target_cgpa <= max_value):
        raise ValueError(f"Target {grading_scale} must be between 0 and {max_value}")
    if credits_completed < 0:
        raise ValueError("Credits completed cannot be negative")
    if credits_remaining < 0:
        raise ValueError("Credits remaining cannot be negative")
    if credits_completed + credits_remaining == 0:
        raise ValueError("Total credits (completed + remaining) cannot be zero")

    # Convert to a common scale (CGPA) for internal calculation
    if grading_scale == 'percentage':
        # Using a more realistic conversion: Percentage = CGPA * 9.5 (common in Indian universities)
        # So, CGPA = Percentage / 9.5
        current_cgpa_internal = current_cgpa / 9.5
        target_cgpa_internal = target_cgpa / 9.5
    else:
        current_cgpa_internal = current_cgpa
        target_cgpa_internal = target_cgpa

    # Total points earned so far
    total_points_earned = current_cgpa_internal * credits_completed

    # Total points needed for target
    total_credits = credits_completed + credits_remaining
    total_points_needed = target_cgpa_internal * total_credits

    # Points needed from remaining courses
    required_points = total_points_needed - total_points_earned

    # Handle case where there are no remaining credits
    if credits_remaining == 0:
        return None  # Cannot calculate required average; no remaining credits

    # Average required CGPA for remaining courses
    required_avg_internal = required_points / credits_remaining

    # Convert back to the original scale
    if grading_scale == 'percentage':
        required_avg = required_avg_internal * 9.5  # Convert CGPA back to percentage
    else:
        required_avg = required_avg_internal

    # Ensure the result is within valid bounds
    return max(0, min(required_avg, max_value))