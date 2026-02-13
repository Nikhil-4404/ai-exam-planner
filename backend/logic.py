import datetime

def calculate_topic_urgency(topic, subject_difficulty, days_remaining):
    """
    Calculates urgency using Modified Ebbinghaus Forgetting Curve logic.
    Score = (Unfamiliarity * Difficulty * ExamUrgency)
    """
    # 1. Exam Urgency (The closer the exam, the higher the score)
    # Avoid div by zero, minimum 1 day
    days_to_exam = max(1, days_remaining)
    # Square root curve for smoother urgency ramp-up
    urgency_factor = 10.0 / (days_to_exam ** 0.5) 

    # 2. Subject Difficulty Multiplier (1.0 to 2.0)
    difficulty_mult = 1.0 + (subject_difficulty / 10.0)

    # 3. Spaced Repetition / Decay Factor (Simulated)
    # Higher weightage topics have a higher "cost" if forgotten.
    decay_weight = topic.weightage 

    # Final Score Combination
    score = (decay_weight * difficulty_mult) * urgency_factor
    
    return score

def get_study_plan(subjects_data, daily_hours):
    """
    Generates a granular plan allocating time to specific topics.
    subjects_data: List of Subject objects (SQLAlchemy models)
    """
    today = datetime.date.today()
    all_pending_items = []
    total_system_urgency = 0.0

    for sub in subjects_data:
        # Calculate days remaining
        days_left = (sub.exam_date - today).days
        days_left = max(1, days_left)

        for topic in sub.topics:
            if not topic.status: # If not done
                urgency = calculate_topic_urgency(topic, sub.difficulty, days_left)
                total_system_urgency += urgency
                all_pending_items.append({
                    "subject": sub.name,
                    "topic": topic.name,
                    "urgency": urgency,
                    "date": sub.exam_date,
                    "topic_obj": topic
                })

    plan_data = []

    if not all_pending_items:
        return []

    # Sort items by urgency
    all_pending_items.sort(key=lambda x: x['urgency'], reverse=True)

    for item in all_pending_items:
        if total_system_urgency > 0:
            allocation = (item['urgency'] / total_system_urgency) * daily_hours
            
            # Rule: Cap max time per topic (max 2 hours)
            # Rule: Min time (min 15 mins)
            if allocation < 0.25: allocation = 0.0
            
            # Round to nearest 0.25
            allocation = round(allocation * 4) / 4
            
            if allocation > 0:
                # Deduce Reason
                days_until = (item['date'] - today).days
                reason = "Balanced Review"
                if days_until <= 3:
                     reason = f"🚨 URGENT: Exam in {days_until} days!"
                elif item['urgency'] > 1.0: 
                     reason = "🔥 Focus: High Difficulty/Weight"
                
                plan_data.append({
                    "subject": item['subject'],
                    "topic": item['topic'],
                    "allocated_hours": allocation,
                    "urgency_score": round(item['urgency'], 2),
                    "exam_date": item['date'],
                    "reason": reason 
                })

    return plan_data
