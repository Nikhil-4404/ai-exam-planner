import datetime

class Topic:
    def __init__(self, name, weightage=1.0, is_completed=False, id=None):
        self.id = id
        self.name = name
        self.weightage = weightage 
        self.is_completed = is_completed

class Subject:
    def __init__(self, name, difficulty, exam_date, topics=None, id=None):
        self.id = id
        self.name = name
        self.difficulty = difficulty  # 1-10
        
        if isinstance(exam_date, str):
            self.exam_date = datetime.datetime.strptime(exam_date, "%Y-%m-%d").date()
        else:
            self.exam_date = exam_date
            
        self.topics = topics if topics else []

    @property
    def topics_remaining(self):
        return [t for t in self.topics if not t.is_completed]

    @property
    def days_remaining(self):
        today = datetime.date.today()
        delta = (self.exam_date - today).days
        return max(1, delta) 

    def calculate_topic_urgency(self, topic):
        """
        Calculates urgency for a SINGLE topic within this subject.
        Formula: (TopicWeight * SubjectDifficulty) / DaysRemaining
        """
        # Base multiplier from 1.0 (at diff 0) to 2.0 (at diff 10)
        diff_multiplier = 1.0 + (self.difficulty / 10.0)
        
        score = (topic.weightage * diff_multiplier) / self.days_remaining
        return score

def get_study_plan_data(subjects, daily_hours):
    """
    Generates a granular plan allocating time to specific topics.
    """
    # 1. Gather ALL pending topics across ALL subjects
    all_pending_items = []
    total_system_urgency = 0.0

    for sub in subjects:
        for topic in sub.topics_remaining:
            urgency = sub.calculate_topic_urgency(topic)
            total_system_urgency += urgency
            all_pending_items.append({
                "subject": sub.name,
                "topic": topic.name,
                "urgency": urgency,
                "date": sub.exam_date
            })

    plan_data = []

    # 2. Check if user is free
    if not all_pending_items:
        return []

    # 3. Allocate time
    # We sort items by urgency to ensure high priority stuff gets listed first
    all_pending_items.sort(key=lambda x: x['urgency'], reverse=True)

    for item in all_pending_items:
        if total_system_urgency > 0:
            allocation = (item['urgency'] / total_system_urgency) * daily_hours
            
            # Rule: Cap max time per topic to avoid burnout on one thing (max 2 hours)
            # Rule: Min time to be useful (min 15 mins), otherwise it might be too granular
            if allocation < 0.25: allocation = 0.0 # Skip negligible tasks
            
            # Round clean
            allocation = round(allocation * 4) / 4
            
            if allocation > 0:
                plan_data.append({
                    "Subject": item['subject'],
                    "Topic": item['topic'],
                    "Allocated Hours": allocation,
                    "Urgency Score": round(item['urgency'], 2),
                    "Exam Date": item['date']
                })

    return plan_data

def generate_plan(subjects, daily_hours):
    # Wrapper for CLI
    print(f"--- Generating Graluar Plan for {datetime.date.today()} ---")
    data = get_study_plan_data(subjects, daily_hours)
    
    if not data:
        print("No pending topics found! Great job.")
        return

    print(f"{'Subject':<15} | {'Topic':<20} | {'Hours':<10} | {'Score'}")
    print("-" * 65)
    for p in data:
        print(f"{p['Subject']:<15} | {p['Topic']:<20} | {p['Allocated Hours']:<10} | {p['Urgency Score']}")

if __name__ == "__main__":
    # Test Data
    math = Subject("Math", 8, "2026-02-15", [
        Topic("Algebra", 1.5), # High weight
        Topic("Geometry", 1.0),
        Topic("Trig", 1.0, is_completed=True)
    ])
    
    physics = Subject("Physics", 5, "2026-02-10", [
        Topic("Kinematics", 1.0),
        Topic("Dynamics", 1.2)
    ])

    generate_plan([math, physics], 6.0)
