import datetime

def calculate_topic_urgency(topic, subject_difficulty, days_remaining):
    """
    Calculates urgency for a SINGLE topic.
    Formula: (TopicWeight * SubjectDifficulty) / DaysRemaining
    """
    # Base multiplier from 1.0 (at diff 0) to 2.0 (at diff 10)
    diff_multiplier = 1.0 + (subject_difficulty / 10.0)
    
    # Avoid division by zero
    effective_days = max(1, days_remaining)
    
    score = (topic.weightage * diff_multiplier) / effective_days
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
                plan_data.append({
                    "subject": item['subject'],
                    "topic": item['topic'],
                    "allocated_hours": allocation,
                    "urgency_score": round(item['urgency'], 2),
                    "exam_date": item['date']
                })

    return plan_data
