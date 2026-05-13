from app.config import WW_WEIGHT, PT_WEIGHT, QA_WEIGHT

def calculate_weighted_grade(db, student_id: str, subject_id: str, term: str) -> float:
    """
    Calculates the final grade for a student in a specific subject and term.
    Formula: (WW_Score * Weight) + (PT_Score * Weight) + (QA_Score * Weight)
    """
    conn = db.connect()
    
    # 1. Fetch subject weights (default to config if not customized in DB)
    subject_row = conn.execute(
        "SELECT ww_weight, pt_weight, qa_weight FROM subjects WHERE id = ?", 
        (subject_id,)
    ).fetchone()
    
    weights = {
        'WW': subject_row['ww_weight'] if subject_row else WW_WEIGHT,
        'PT': subject_row['pt_weight'] if subject_row else PT_WEIGHT,
        'QA': subject_row['qa_weight'] if subject_row else QA_WEIGHT
    }

    final_weighted_score = 0.0

    # 2. Calculate totals for each category
    for category in ['WW', 'PT', 'QA']:
        # Join entries with columns to filter by category and sum up scores
        query = """
            SELECT 
                SUM(e.score) as earned, 
                SUM(c.max_score) as total_max
            FROM grade_entries e
            JOIN grade_columns c ON e.column_id = c.id
            WHERE e.student_id = ? 
              AND c.subject_id = ? 
              AND c.term = ? 
              AND c.category = ?
        """
        result = conn.execute(query, (student_id, subject_id, term, category)).fetchone()
        
        earned = result['earned'] if result and result['earned'] is not None else 0
        total_max = result['total_max'] if result and result['total_max'] else 0
        
        if total_max > 0:
            # DepEd Standard: (Earned / Max) * 100
            percentage_score = (earned / total_max) * 100
            # Apply category weight (e.g., 40% -> 0.40)
            weighted_score = percentage_score * weights[category]
            final_weighted_score += weighted_score

    return round(final_weighted_score, 2)