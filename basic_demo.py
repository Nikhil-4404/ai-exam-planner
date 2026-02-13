import datetime

# --- 1. Basic Data Structures ---
# In the beginning, we just used simple dictionaries to hold specific subject info
subjects = [
    {"name": "Artificial Intelligence", "difficulty": 8, "exam_date": "2026-03-10", "topics": ["Search Algos", "Neural Nets", "NLP"]},
    {"name": "Web Development",       "difficulty": 4, "exam_date": "2026-03-05", "topics": ["React", "CSS Grid", "APIs"]},
    {"name": "Data Structures",       "difficulty": 9, "exam_date": "2026-03-15", "topics": ["Trees", "Graphs", "DP"]}
]

def calculate_urgency(subject, today):
    """
    The Core Logic: 
    Urgency = (Difficulty * Weight) / Days_Left
    """
    exam_date = datetime.datetime.strptime(subject["exam_date"], "%Y-%m-%d").date()
    days_left = (exam_date - today).days
    
    if days_left <= 0:
        return 9999 # Panic mode!
        
    # Heuristic: Harder subjects need more attention per day
    urgency_score = subject["difficulty"] / days_left
    return urgency_score, days_left

def generate_simple_plan(daily_hours_available=4):
    print(f"\n🎓 BASIC EXAM PLANNER DEMO")
    print(f"📅 Today: {datetime.date.today()}")
    print("-" * 40)
    
    today = datetime.date.today()
    study_queue = []

    # 1. Calculate scores for all subjects
    for sub in subjects:
        score, days = calculate_urgency(sub, today)
        study_queue.append({
            "name": sub["name"],
            "score": score,
            "days_left": days,
            "topics": sub["topics"]
        })

    # 2. Sort by Urgency (Highest first)
    study_queue.sort(key=lambda x: x["score"], reverse=True)

    # 3. Allocate Time
    print(f"\n⚡ TODAY'S STRATEGY ({daily_hours_available} hours available):\n")
    
    total_score = sum(s["score"] for s in study_queue)
    
    for item in study_queue:
        if total_score > 0:
            # Proportional allocation
            hours = (item["score"] / total_score) * daily_hours_available
            hours = round(hours, 1) # Round to 1 decimal
        else:
            hours = 0
            
        status_icon = "🟢"
        if item["score"] > 1.0: status_icon = "🟠"
        if item["score"] > 2.0: status_icon = "🔴"

        print(f"{status_icon} {item['name']}")
        print(f"   • Exam in: {item['days_left']} days")
        print(f"   • Urgency Score: {item['score']:.2f}")
        print(f"   • Study Time: {hours} hours")
        print(f"   • Focus Topic: {item['topics'][0]}") # Just pick first topic for demo
        print("-" * 30)

if __name__ == "__main__":
    # Simulate a user login input
    print("Welcome! Please Login.")
    user = input("Username (press Enter for 'student'): ") or "student"
    print(f"\nHello, {user}! Generating your study plan...\n")
    
    generate_simple_plan()
