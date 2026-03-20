import { useEffect, useState } from 'react'
import './App.css'

type StudyStyle = 'Balanced' | 'Concept-first' | 'Practice-heavy'
type MilestoneStatus = 'Pending' | 'In progress' | 'Done'

type PlannerProfile = {
  examName: string
  targetDate: string
  weeklyHours: number
  targetScore: number
  confidenceLevel: number
  stressLevel: number
  studyStyle: StudyStyle
}

type Subject = {
  id: string
  name: string
  priority: number
  currentLevel: number
  targetLevel: number
  syllabusCoverage: number
  mockScore: number
}

type Milestone = {
  id: string
  title: string
  dueDate: string
  status: MilestoneStatus
}

const storageKey = 'exam-strategy-planner:v1'

const today = new Date()
const oneDayMs = 24 * 60 * 60 * 1000

const formatDateInput = (date: Date) => date.toISOString().slice(0, 10)

const addDays = (date: Date, days: number) => {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

const createId = () =>
  `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`

const defaultProfile: PlannerProfile = {
  examName: 'UPSC Prelims 2026',
  targetDate: formatDateInput(addDays(today, 120)),
  weeklyHours: 24,
  targetScore: 82,
  confidenceLevel: 58,
  stressLevel: 43,
  studyStyle: 'Balanced',
}

const defaultSubjects: Subject[] = [
  {
    id: createId(),
    name: 'Polity',
    priority: 5,
    currentLevel: 61,
    targetLevel: 88,
    syllabusCoverage: 52,
    mockScore: 64,
  },
  {
    id: createId(),
    name: 'Modern History',
    priority: 4,
    currentLevel: 56,
    targetLevel: 82,
    syllabusCoverage: 47,
    mockScore: 58,
  },
  {
    id: createId(),
    name: 'Environment & Ecology',
    priority: 5,
    currentLevel: 48,
    targetLevel: 80,
    syllabusCoverage: 38,
    mockScore: 46,
  },
]

const defaultMilestones: Milestone[] = [
  {
    id: createId(),
    title: 'Complete first syllabus sweep',
    dueDate: formatDateInput(addDays(today, 21)),
    status: 'In progress',
  },
  {
    id: createId(),
    title: 'Finish 5 full-length mock tests',
    dueDate: formatDateInput(addDays(today, 45)),
    status: 'Pending',
  },
  {
    id: createId(),
    title: 'Run revision-only final sprint',
    dueDate: formatDateInput(addDays(today, 95)),
    status: 'Pending',
  },
]

const getStoredState = () => {
  if (typeof window === 'undefined') {
    return null
  }

  try {
    const raw = window.localStorage.getItem(storageKey)

    if (!raw) {
      return null
    }

    return JSON.parse(raw) as {
      profile: PlannerProfile
      subjects: Subject[]
      milestones: Milestone[]
    }
  } catch {
    return null
  }
}

const clamp = (value: number, min: number, max: number) =>
  Math.min(max, Math.max(min, value))

function App() {
  const stored = getStoredState()
  const [profile, setProfile] = useState<PlannerProfile>(
    stored?.profile ?? defaultProfile,
  )
  const [subjects, setSubjects] = useState<Subject[]>(
    stored?.subjects ?? defaultSubjects,
  )
  const [milestones, setMilestones] = useState<Milestone[]>(
    stored?.milestones ?? defaultMilestones,
  )
  const [newSubject, setNewSubject] = useState({
    name: '',
    priority: 3,
    currentLevel: 50,
    targetLevel: 80,
    syllabusCoverage: 35,
    mockScore: 50,
  })
  const [newMilestone, setNewMilestone] = useState({
    title: '',
    dueDate: formatDateInput(addDays(today, 14)),
    status: 'Pending' as MilestoneStatus,
  })

  useEffect(() => {
    window.localStorage.setItem(
      storageKey,
      JSON.stringify({ profile, subjects, milestones }),
    )
  }, [profile, subjects, milestones])

  const targetDate = new Date(profile.targetDate)
  const daysLeft = Math.max(
    0,
    Math.ceil((targetDate.getTime() - today.getTime()) / oneDayMs),
  )
  const weeksLeft = Math.max(1, Math.ceil(daysLeft / 7))

  const subjectStrategies = subjects.map((subject) => {
    const gap = clamp(subject.targetLevel - subject.currentLevel, 0, 100)
    const urgency =
      gap * 0.45 +
      subject.priority * 9 +
      (100 - subject.syllabusCoverage) * 0.25 +
      (100 - subject.mockScore) * 0.21
    const hours = Math.max(
      2,
      Math.round((urgency / Math.max(1, subjects.length * 20)) * profile.weeklyHours),
    )

    let mode = 'Mixed revision + targeted practice'
    if (profile.studyStyle === 'Concept-first' || subject.syllabusCoverage < 45) {
      mode = 'Concept rebuild and short-note creation'
    } else if (profile.studyStyle === 'Practice-heavy' || subject.mockScore < 55) {
      mode = 'Timed drills and post-mock error review'
    }

    return {
      ...subject,
      gap,
      urgency,
      weeklyHours: hours,
      mode,
      readiness: clamp(
        Math.round(
          subject.currentLevel * 0.42 +
            subject.syllabusCoverage * 0.28 +
            subject.mockScore * 0.3,
        ),
        0,
        100,
      ),
    }
  })

  const totalRecommendedHours = subjectStrategies.reduce(
    (sum, subject) => sum + subject.weeklyHours,
    0,
  )

  const normalizedPlan = subjectStrategies.map((subject) => ({
    ...subject,
    normalizedHours: Math.max(
      1,
      Math.round((subject.weeklyHours / totalRecommendedHours) * profile.weeklyHours),
    ),
  }))

  const readinessScore =
    normalizedPlan.length === 0
      ? 0
      : Math.round(
          normalizedPlan.reduce((sum, subject) => sum + subject.readiness, 0) /
            normalizedPlan.length,
        )

  const focusSubject =
    [...normalizedPlan].sort((left, right) => right.urgency - left.urgency)[0] ??
    null

  const completedMilestones = milestones.filter(
    (milestone) => milestone.status === 'Done',
  ).length

  const completionRate =
    milestones.length === 0
      ? 0
      : Math.round((completedMilestones / milestones.length) * 100)

  const examPhase =
    daysLeft > 90
      ? 'Foundation'
      : daysLeft > 45
        ? 'Acceleration'
        : 'Final revision'

  const riskFlags = [
    profile.weeklyHours < 12
      ? 'Your weekly study time is low for an aggressive target. Add at least one protected long session.'
      : null,
    profile.stressLevel > 70
      ? 'Stress is elevated. Keep one low-intensity recovery block and one mock-free evening per week.'
      : null,
    readinessScore < profile.targetScore - 12
      ? 'Readiness is trailing the goal score. Prioritize mocks plus error logs over passive rereading.'
      : null,
  ].filter(Boolean) as string[]

  const sprintLabels = ['Foundation', 'Practice', 'Revision']
  const weeklySprint = sprintLabels.map((label, index) => {
    const ratio = index === 0 ? 0.4 : index === 1 ? 0.35 : 0.25
    return {
      label,
      hours: Math.max(1, Math.round(profile.weeklyHours * ratio)),
    }
  })

  const recoveryMinutes =
    profile.stressLevel > 65 ? 25 : profile.stressLevel > 40 ? 15 : 10

  const exportPlan = () => {
    const lines = [
      `${profile.examName} Strategy Snapshot`,
      `Target date: ${profile.targetDate}`,
      `Exam phase: ${examPhase}`,
      `Readiness score: ${readinessScore}%`,
      `Goal score: ${profile.targetScore}%`,
      '',
      'Subject priorities:',
      ...normalizedPlan
        .sort((left, right) => right.urgency - left.urgency)
        .map(
          (subject) =>
            `- ${subject.name}: ${subject.normalizedHours}h/week, ${subject.mode}, readiness ${subject.readiness}%`,
        ),
      '',
      'Milestones:',
      ...milestones.map(
        (milestone) =>
          `- ${milestone.title} (${milestone.dueDate}) [${milestone.status}]`,
      ),
    ]

    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'exam-strategy-plan.txt'
    anchor.click()
    URL.revokeObjectURL(url)
  }

  const resetPlanner = () => {
    setProfile(defaultProfile)
    setSubjects(defaultSubjects)
    setMilestones(defaultMilestones)
  }

  const addSubject = () => {
    if (!newSubject.name.trim()) {
      return
    }

    setSubjects((current) => [
      ...current,
      {
        id: createId(),
        name: newSubject.name.trim(),
        priority: newSubject.priority,
        currentLevel: newSubject.currentLevel,
        targetLevel: newSubject.targetLevel,
        syllabusCoverage: newSubject.syllabusCoverage,
        mockScore: newSubject.mockScore,
      },
    ])
    setNewSubject({
      name: '',
      priority: 3,
      currentLevel: 50,
      targetLevel: 80,
      syllabusCoverage: 35,
      mockScore: 50,
    })
  }

  const addMilestone = () => {
    if (!newMilestone.title.trim()) {
      return
    }

    setMilestones((current) => [
      ...current,
      {
        id: createId(),
        title: newMilestone.title.trim(),
        dueDate: newMilestone.dueDate,
        status: newMilestone.status,
      },
    ])
    setNewMilestone({
      title: '',
      dueDate: formatDateInput(addDays(today, 14)),
      status: 'Pending',
    })
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <span className="eyebrow">Deployment-ready academic planner</span>
          <h1>Exam Preparation Strategy Planner</h1>
          <p className="hero-text">
            Plan your exam prep like a real campaign: map the target, rank
            weak areas, build weekly execution blocks, and keep the final
            revision window protected.
          </p>
          <div className="hero-actions">
            <button type="button" className="primary-button" onClick={exportPlan}>
              Export strategy brief
            </button>
            <button type="button" className="secondary-button" onClick={resetPlanner}>
              Reset demo data
            </button>
          </div>
        </div>

        <div className="hero-metrics">
          <article className="metric-card accent">
            <span>Days left</span>
            <strong>{daysLeft}</strong>
            <p>{examPhase} mode is active</p>
          </article>
          <article className="metric-card">
            <span>Readiness</span>
            <strong>{readinessScore}%</strong>
            <p>{completionRate}% milestone completion</p>
          </article>
          <article className="metric-card">
            <span>Weekly focus</span>
            <strong>{profile.weeklyHours}h</strong>
            <p>{focusSubject ? `${focusSubject.name} needs the sharpest push` : 'Add a subject to begin'}</p>
          </article>
        </div>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">1. Strategy inputs</span>
              <h2>Exam profile</h2>
            </div>
            <p>These values drive the planner recommendations automatically.</p>
          </div>

          <div className="form-grid">
            <label>
              <span>Exam name</span>
              <input
                value={profile.examName}
                onChange={(event) =>
                  setProfile((current) => ({
                    ...current,
                    examName: event.target.value,
                  }))
                }
                placeholder="e.g. JEE Main 2026"
              />
            </label>

            <label>
              <span>Target date</span>
              <input
                type="date"
                value={profile.targetDate}
                onChange={(event) =>
                  setProfile((current) => ({
                    ...current,
                    targetDate: event.target.value,
                  }))
                }
              />
            </label>

            <label>
              <span>Study hours per week</span>
              <input
                type="number"
                min="1"
                max="80"
                value={profile.weeklyHours}
                onChange={(event) =>
                  setProfile((current) => ({
                    ...current,
                    weeklyHours: Number(event.target.value),
                  }))
                }
              />
            </label>

            <label>
              <span>Target score (%)</span>
              <input
                type="number"
                min="1"
                max="100"
                value={profile.targetScore}
                onChange={(event) =>
                  setProfile((current) => ({
                    ...current,
                    targetScore: Number(event.target.value),
                  }))
                }
              />
            </label>

            <label>
              <span>Study style</span>
              <select
                value={profile.studyStyle}
                onChange={(event) =>
                  setProfile((current) => ({
                    ...current,
                    studyStyle: event.target.value as StudyStyle,
                  }))
                }
              >
                <option>Balanced</option>
                <option>Concept-first</option>
                <option>Practice-heavy</option>
              </select>
            </label>

            <label>
              <span>Confidence level ({profile.confidenceLevel}%)</span>
              <input
                type="range"
                min="1"
                max="100"
                value={profile.confidenceLevel}
                onChange={(event) =>
                  setProfile((current) => ({
                    ...current,
                    confidenceLevel: Number(event.target.value),
                  }))
                }
              />
            </label>

            <label className="full-width">
              <span>Stress level ({profile.stressLevel}%)</span>
              <input
                type="range"
                min="1"
                max="100"
                value={profile.stressLevel}
                onChange={(event) =>
                  setProfile((current) => ({
                    ...current,
                    stressLevel: Number(event.target.value),
                  }))
                }
              />
            </label>
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">2. Priority engine</span>
              <h2>Subject command center</h2>
            </div>
            <p>Track each subject by effort gap, coverage depth, and test output.</p>
          </div>

          <div className="stack">
            {normalizedPlan.map((subject) => (
              <div className="subject-card" key={subject.id}>
                <div className="subject-row">
                  <div>
                    <h3>{subject.name}</h3>
                    <p>{subject.mode}</p>
                  </div>
                  <span className="badge">{subject.normalizedHours}h/week</span>
                </div>
                <div className="subject-stats">
                  <span>Priority {subject.priority}/5</span>
                  <span>Coverage {subject.syllabusCoverage}%</span>
                  <span>Mock {subject.mockScore}%</span>
                  <span>Readiness {subject.readiness}%</span>
                </div>
                <div className="progress-strip">
                  <div style={{ width: `${subject.readiness}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="mini-form">
            <h3>Add subject</h3>
            <div className="form-grid compact">
              <label>
                <span>Name</span>
                <input
                  value={newSubject.name}
                  onChange={(event) =>
                    setNewSubject((current) => ({
                      ...current,
                      name: event.target.value,
                    }))
                  }
                  placeholder="e.g. Physics"
                />
              </label>
              <label>
                <span>Priority</span>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={newSubject.priority}
                  onChange={(event) =>
                    setNewSubject((current) => ({
                      ...current,
                      priority: Number(event.target.value),
                    }))
                  }
                />
              </label>
              <label>
                <span>Current level</span>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={newSubject.currentLevel}
                  onChange={(event) =>
                    setNewSubject((current) => ({
                      ...current,
                      currentLevel: Number(event.target.value),
                    }))
                  }
                />
              </label>
              <label>
                <span>Target level</span>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={newSubject.targetLevel}
                  onChange={(event) =>
                    setNewSubject((current) => ({
                      ...current,
                      targetLevel: Number(event.target.value),
                    }))
                  }
                />
              </label>
              <label>
                <span>Syllabus coverage</span>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={newSubject.syllabusCoverage}
                  onChange={(event) =>
                    setNewSubject((current) => ({
                      ...current,
                      syllabusCoverage: Number(event.target.value),
                    }))
                  }
                />
              </label>
              <label>
                <span>Mock score</span>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={newSubject.mockScore}
                  onChange={(event) =>
                    setNewSubject((current) => ({
                      ...current,
                      mockScore: Number(event.target.value),
                    }))
                  }
                />
              </label>
            </div>
            <button type="button" className="secondary-button" onClick={addSubject}>
              Add subject
            </button>
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">3. Weekly execution</span>
              <h2>Study sprint design</h2>
            </div>
            <p>Convert your weekly hours into repeatable blocks with clear intent.</p>
          </div>

          <div className="sprint-grid">
            {weeklySprint.map((sprint) => (
              <article key={sprint.label} className="sprint-card">
                <span>{sprint.label}</span>
                <strong>{sprint.hours}h</strong>
                <p>
                  {sprint.label === 'Foundation' && 'Build concepts, compress notes, and lock key formulas.'}
                  {sprint.label === 'Practice' && 'Run timed sets, analyze misses, and rebuild weak chapters.'}
                  {sprint.label === 'Revision' && 'Use flash review, error logs, and rapid recall drills.'}
                </p>
              </article>
            ))}
          </div>

          <div className="agenda-card">
            <h3>Daily operating rhythm</h3>
            <ul className="agenda-list">
              <li>Start with a 20-minute recall warm-up from yesterday's errors.</li>
              <li>Spend the first deep-work block on {focusSubject?.name ?? 'your highest-risk subject'}.</li>
              <li>Reserve {recoveryMinutes} minutes for recovery and spaced repetition at the end.</li>
            </ul>
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">4. Milestones</span>
              <h2>Checkpoint tracker</h2>
            </div>
            <p>Keep the syllabus, mock cycle, and revision runway visible.</p>
          </div>

          <div className="stack">
            {milestones.map((milestone) => (
              <div className="milestone-card" key={milestone.id}>
                <div>
                  <h3>{milestone.title}</h3>
                  <p>Due {milestone.dueDate}</p>
                </div>
                <select
                  value={milestone.status}
                  onChange={(event) =>
                    setMilestones((current) =>
                      current.map((entry) =>
                        entry.id === milestone.id
                          ? {
                              ...entry,
                              status: event.target.value as MilestoneStatus,
                            }
                          : entry,
                      ),
                    )
                  }
                >
                  <option>Pending</option>
                  <option>In progress</option>
                  <option>Done</option>
                </select>
              </div>
            ))}
          </div>

          <div className="mini-form">
            <h3>Add milestone</h3>
            <div className="form-grid compact">
              <label className="full-width">
                <span>Title</span>
                <input
                  value={newMilestone.title}
                  onChange={(event) =>
                    setNewMilestone((current) => ({
                      ...current,
                      title: event.target.value,
                    }))
                  }
                  placeholder="e.g. Complete chapter-wise test cycle"
                />
              </label>
              <label>
                <span>Due date</span>
                <input
                  type="date"
                  value={newMilestone.dueDate}
                  onChange={(event) =>
                    setNewMilestone((current) => ({
                      ...current,
                      dueDate: event.target.value,
                    }))
                  }
                />
              </label>
              <label>
                <span>Status</span>
                <select
                  value={newMilestone.status}
                  onChange={(event) =>
                    setNewMilestone((current) => ({
                      ...current,
                      status: event.target.value as MilestoneStatus,
                    }))
                  }
                >
                  <option>Pending</option>
                  <option>In progress</option>
                  <option>Done</option>
                </select>
              </label>
            </div>
            <button
              type="button"
              className="secondary-button"
              onClick={addMilestone}
            >
              Add milestone
            </button>
          </div>
        </article>

        <article className="panel span-two">
          <div className="panel-header">
            <div>
              <span className="panel-kicker">5. Coach view</span>
              <h2>Strategy summary</h2>
            </div>
            <p>High-signal guidance for the next study cycle.</p>
          </div>

          <div className="summary-grid">
            <article className="summary-card">
              <span>Primary pressure point</span>
              <strong>{focusSubject?.name ?? 'No subject added yet'}</strong>
              <p>
                {focusSubject
                  ? `${focusSubject.mode}. Close a ${focusSubject.gap}% gap before the next mock.`
                  : 'Start by adding your core subjects and difficulty levels.'}
              </p>
            </article>
            <article className="summary-card">
              <span>Confidence vs reality</span>
              <strong>{profile.confidenceLevel}% confidence</strong>
              <p>
                Keep confidence grounded in evidence: one mock, one review, one
                adjusted plan each week.
              </p>
            </article>
            <article className="summary-card">
              <span>Revision runway</span>
              <strong>{Math.max(2, Math.round(weeksLeft * 0.3))} weeks</strong>
              <p>
                Protect this final block for condensed notes, repeated mistakes,
                and full-length mock rehearsals.
              </p>
            </article>
          </div>

          {riskFlags.length > 0 ? (
            <div className="risk-board">
              {riskFlags.map((flag) => (
                <p key={flag}>{flag}</p>
              ))}
            </div>
          ) : (
            <div className="risk-board safe">
              <p>Your current plan is balanced. Stay consistent and keep mock analysis non-negotiable.</p>
            </div>
          )}
        </article>
      </section>
    </main>
  )
}

export default App
