import datetime

class Subject:
    def __init__(self, name, difficulty, chapters_total, chapters_done, exam_date):
        self.name = name
        self.difficulty = difficulty  # 1-10
        self.chapters_total = chapters_total
        self.chapters_done = chapters_done
        if isinstance(exam_date, str):
            self.exam_date = datetime.datetime.strptime(exam_date, "%Y-%m-%d").date()
        else:
            self.exam_date = exam_date

    @property
    def chapters_remaining(self):
        return max(0, self.chapters_total - self.chapters_done)

    @property
    def days_remaining(self):
        today = datetime.date.today()
        # If exam is in the past, treat as 1 day (Urgent!) 
        delta = (self.exam_date - today).days
        return max(1, delta) 

    def calculate_urgency(self):
        # Heuristic: (Difficulty * Chapters Left) / Days Left
        # We use a base weight of 1.0 so even Difficulty 0 gets scheduled if work remains
        # Formula: Weight ranges from 1.0 (Diff 0) to 2.0 (Diff 10)
        weight = 1.0 + (self.difficulty / 10.0)
        score = (self.chapters_remaining * weight) / self.days_remaining
        return score

def get_study_plan_data(subjects, daily_hours):
    """
    Core functional logic that returns the plan data structure.
    Used by both the CLI (wrapper) and the Web UI.
    """
    total_urgency = sum(s.calculate_urgency() for s in subjects)
    plan_data = []

    for sub in subjects:
        urgency = sub.calculate_urgency()
        allocation = 0.0
        note = ""

        if sub.chapters_remaining == 0:
            note = "✅ 100% Complete"
            urgency = 0 
        elif urgency > 0 and total_urgency > 0:
            allocation = (urgency / total_urgency) * daily_hours
            allocation = round(allocation * 4) / 4
        
        plan_data.append({
            "Subject": sub.name,
            "Allocated Hours": allocation,
            "Urgency Score": round(urgency, 2),
            "Status Note": note,
            "Exam Date": sub.exam_date
        })

    # Sort by urgency
    plan_data.sort(key=lambda x: x["Urgency Score"], reverse=True)
    return plan_data

def generate_plan(subjects, daily_hours):
    # Wrapper for CLI
    print(f"--- Generating Plan for {datetime.date.today()} ---")
    print(f"Available Time: {daily_hours} hours\n") # Added this back for full backward compatibility
    data = get_study_plan_data(subjects, daily_hours)
    
    print(f"{'Subject':<15} | {'Hours':<10} | {'Urgency Score':<15} | {'Note'}")
    print("-" * 65)
    for p in data:
        hours_str = str(p['Allocated Hours']) if p['Allocated Hours'] > 0 else "-"
        print(f"{p['Subject']:<15} | {hours_str:<10} | {p['Urgency Score']:.2f}             | {p['Status Note']}")

# Example Usage
if __name__ == "__main__":
    my_subjects = [
        Subject("Mathematics", difficulty=4, chapters_total=20, chapters_done=20, exam_date="2026-02-15"),
        Subject("History", difficulty=2, chapters_total=15, chapters_done=4, exam_date="2026-02-01"),
        Subject("Physics", difficulty=0, chapters_total=18, chapters_done=0, exam_date="2026-02-10"),
    ]

    generate_plan(my_subjects, daily_hours=6.0)
