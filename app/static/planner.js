const defaultSubjects = [
  {
    name: "Polity",
    priority: 5,
    current_level: 61,
    target_level: 88,
    syllabus_coverage: 52,
    mock_score: 64,
  },
  {
    name: "Modern History",
    priority: 4,
    current_level: 56,
    target_level: 82,
    syllabus_coverage: 47,
    mock_score: 58,
  },
  {
    name: "Environment & Ecology",
    priority: 5,
    current_level: 48,
    target_level: 80,
    syllabus_coverage: 38,
    mock_score: 46,
  },
];

const subjectsRoot = document.querySelector("#subjects");
const plannerForm = document.querySelector("#planner-form");
const addSubjectButton = document.querySelector("#add-subject");
const resetDemoButton = document.querySelector("#reset-demo");
const summaryNode = document.querySelector("#summary");
const statusPill = document.querySelector("#status-pill");
const focusSubjectsNode = document.querySelector("#focus-subjects");
const nextStepsNode = document.querySelector("#next-steps");
const weeklyPlanNode = document.querySelector("#weekly-plan");
const riskAlertsNode = document.querySelector("#risk-alerts");
const logoutButton = document.querySelector("#logout-button");
const authStatus = document.querySelector("#auth-status");
const savedPlansNode = document.querySelector("#saved-plans");
const savePlanButton = document.querySelector("#save-plan");
const exportCurrentPdfButton = document.querySelector("#export-current-pdf");
const plannerChartNode = document.querySelector("#planner-chart");
const plannerPillRowNode = document.querySelector("#planner-pill-row");
const plannerLinePrimaryNode = document.querySelector("#planner-line-primary");
const plannerLineSecondaryNode = document.querySelector("#planner-line-secondary");
const plannerLinePrimaryValueNode = document.querySelector("#planner-line-primary-value");
const plannerLineSecondaryValueNode = document.querySelector("#planner-line-secondary-value");

let currentPayload = null;
let currentStrategy = null;

const defaultChartHeights = [42, 68, 54, 88, 72];

const buildPreviewPayload = () => {
  try {
    return buildPayload();
  } catch {
    return null;
  }
};

const setDefaultDate = () => {
  const targetInput = plannerForm.querySelector('input[name="target_date"]');
  const targetDate = new Date();
  targetDate.setDate(targetDate.getDate() + 120);
  targetInput.value = targetDate.toISOString().slice(0, 10);
};

const subjectCard = (subject = {}) => {
  const wrapper = document.createElement("article");
  wrapper.className = "subject-card";
  wrapper.innerHTML = `
    <div class="subject-grid">
      <label><span>Subject</span><input name="name" value="${subject.name ?? ""}" required /></label>
      <label><span>Priority</span><input name="priority" type="number" min="1" max="5" value="${subject.priority ?? 3}" required /></label>
      <label><span>Current level</span><input name="current_level" type="number" min="0" max="100" value="${subject.current_level ?? 50}" required /></label>
      <label><span>Target level</span><input name="target_level" type="number" min="0" max="100" value="${subject.target_level ?? 80}" required /></label>
      <label><span>Syllabus coverage</span><input name="syllabus_coverage" type="number" min="0" max="100" value="${subject.syllabus_coverage ?? 35}" required /></label>
      <label><span>Mock score</span><input name="mock_score" type="number" min="0" max="100" value="${subject.mock_score ?? 50}" required /></label>
    </div>
    <button type="button" class="ghost-button remove-subject">Remove</button>
  `;
  wrapper.querySelector(".remove-subject").addEventListener("click", () => wrapper.remove());
  return wrapper;
};

const seedSubjects = (subjects = defaultSubjects) => {
  subjectsRoot.innerHTML = "";
  subjects.forEach((subject) => subjectsRoot.appendChild(subjectCard(subject)));
};

const readSubjects = () =>
  [...subjectsRoot.querySelectorAll(".subject-card")]
    .map((card) => {
      const read = (name) => card.querySelector(`[name="${name}"]`).value;
      return {
        name: read("name").trim(),
        priority: Number(read("priority")),
        current_level: Number(read("current_level")),
        target_level: Number(read("target_level")),
        syllabus_coverage: Number(read("syllabus_coverage")),
        mock_score: Number(read("mock_score")),
      };
    })
    .filter((subject) => subject.name);

const buildPayload = () => {
  const formData = new FormData(plannerForm);
  return {
    exam_name: formData.get("exam_name"),
    target_date: formData.get("target_date"),
    weekly_hours: Number(formData.get("weekly_hours")),
    target_score: Number(formData.get("target_score")),
    confidence_level: Number(formData.get("confidence_level")),
    stress_level: Number(formData.get("stress_level")),
    study_style: formData.get("study_style"),
    constraints: formData.get("constraints"),
    subjects: readSubjects(),
  };
};

const populateForm = (payload) => {
  plannerForm.querySelector('[name="exam_name"]').value = payload.exam_name;
  plannerForm.querySelector('[name="target_date"]').value = payload.target_date;
  plannerForm.querySelector('[name="weekly_hours"]').value = payload.weekly_hours;
  plannerForm.querySelector('[name="target_score"]').value = payload.target_score;
  plannerForm.querySelector('[name="confidence_level"]').value = payload.confidence_level;
  plannerForm.querySelector('[name="stress_level"]').value = payload.stress_level;
  plannerForm.querySelector('[name="study_style"]').value = payload.study_style;
  plannerForm.querySelector('[name="constraints"]').value = payload.constraints ?? "";
  seedSubjects(payload.subjects ?? []);
};

const renderList = (node, items) => {
  node.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    node.appendChild(li);
  });
};

const renderChips = (items) => {
  focusSubjectsNode.innerHTML = "";
  items.forEach((item) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = item;
    focusSubjectsNode.appendChild(chip);
  });
};

const setStatus = (text, variant = "idle") => {
  statusPill.textContent = text;
  statusPill.dataset.variant = variant;
};

const renderPlannerVisual = (payload = null, strategy = null) => {
  if (!plannerChartNode || !plannerPillRowNode || !plannerLinePrimaryNode || !plannerLineSecondaryNode) {
    return;
  }

  let chartHeights = [...defaultChartHeights];
  let chartLabels = ["Subject A", "Subject B", "Subject C", "Subject D", "Subject E"];
  let pills = ["Priority subjects", "Weekly sprint", "Risk alerts"];
  let primaryWidth = "92%";
  let secondaryWidth = "72%";
  let readinessValue = 72;
  let coverageValue = 58;

  if (payload) {
    const rankedSubjects = payload.subjects
      .map((subject) => {
        const gap = Math.max(subject.target_level - subject.current_level, 0);
        const pressure =
          gap * 0.45 +
          subject.priority * 10 +
          (100 - subject.syllabus_coverage) * 0.23 +
          (100 - subject.mock_score) * 0.22;
        const readiness =
          subject.current_level * 0.45 +
          subject.mock_score * 0.35 +
          subject.syllabus_coverage * 0.2;
        return {
          ...subject,
          pressure,
          readiness,
        };
      })
      .sort((left, right) => right.pressure - left.pressure);

    chartHeights = rankedSubjects.slice(0, 5).map((subject) => {
      const normalized = Math.round(Math.min(88, Math.max(32, subject.pressure)));
      return normalized;
    });
    chartLabels = rankedSubjects.slice(0, 5).map((subject) => subject.name);

    if (strategy) {
      pills = [
        strategy.focus_subjects?.[0] || "Priority subjects",
        strategy.weekly_plan?.[0]?.split(":")[0] || "Weekly sprint",
        strategy.risk_alerts?.[0]?.split(".")[0] || "Risk alerts",
      ];
    } else {
      pills = [
        rankedSubjects[0]?.name || "Priority subjects",
        "Weekly sprint",
        "Risk alerts",
      ];
    }

    readinessValue = Math.round(
      rankedSubjects.reduce((sum, subject) => sum + subject.readiness, 0) /
        Math.max(rankedSubjects.length, 1),
    );
    coverageValue = Math.round(
      rankedSubjects.reduce((sum, subject) => sum + subject.syllabus_coverage, 0) /
        Math.max(rankedSubjects.length, 1),
    );

    primaryWidth = `${Math.max(18, Math.min(100, readinessValue))}%`;
    secondaryWidth = `${Math.max(18, Math.min(100, coverageValue))}%`;
  }

  plannerLinePrimaryNode.style.width = primaryWidth;
  plannerLineSecondaryNode.style.width = secondaryWidth;
  if (plannerLinePrimaryValueNode) {
    plannerLinePrimaryValueNode.textContent = `${readinessValue}%`;
  }
  if (plannerLineSecondaryValueNode) {
    plannerLineSecondaryValueNode.textContent = `${coverageValue}%`;
  }

  plannerPillRowNode.innerHTML = "";
  pills.forEach((pill) => {
    const pillNode = document.createElement("span");
    pillNode.textContent = pill;
    plannerPillRowNode.appendChild(pillNode);
  });

  plannerChartNode.innerHTML = "";
  chartHeights.forEach((height, index) => {
    const item = document.createElement("div");
    item.className = "planner-chart-item";

    const value = document.createElement("span");
    value.className = "planner-bar-value";
    value.textContent = `${height}`;

    const barArea = document.createElement("div");
    barArea.className = "planner-bar-area";

    const bar = document.createElement("span");
    bar.className = "planner-bar";
    bar.style.height = `${height}%`;
    bar.style.animationDelay = `${index * 80}ms`;
    bar.title = `${chartLabels[index]}: ${height}`;

    const label = document.createElement("span");
    label.className = "planner-bar-label";
    label.textContent = chartLabels[index];
    label.title = chartLabels[index];

    item.appendChild(value);
    barArea.appendChild(bar);
    item.appendChild(barArea);
    item.appendChild(label);
    plannerChartNode.appendChild(item);
  });
};

const renderStrategy = (result) => {
  currentStrategy = result;
  summaryNode.textContent = result.summary;
  renderList(nextStepsNode, result.next_steps);
  renderList(weeklyPlanNode, result.weekly_plan);
  renderList(riskAlertsNode, result.risk_alerts);
  renderChips(result.focus_subjects);
  renderPlannerVisual(currentPayload, result);
  setStatus(
    result.mode === "ai" ? `AI strategy ready via ${result.model}` : "Fallback strategy ready",
    result.mode === "ai" ? "success" : "fallback",
  );
};

const postJson = async (url, payload) => {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    if (response.status === 401) {
      window.location.href = "/login";
      return null;
    }
    const error = await response.json().catch(() => ({ detail: "Request failed." }));
    throw new Error(error.detail || "Request failed.");
  }

  return response.status === 204 ? null : response.json();
};

const renderSavedPlans = (plans) => {
  savedPlansNode.innerHTML = "";

  if (!plans.length) {
    savedPlansNode.className = "saved-plans empty-state";
    savedPlansNode.textContent = "No saved plans yet. Generate one and save it.";
    return;
  }

  savedPlansNode.className = "saved-plans";
  plans.forEach((plan) => {
    const card = document.createElement("article");
    card.className = "saved-plan-card";
    card.innerHTML = `
      <div>
        <h3>${plan.title}</h3>
        <p>${plan.exam_name} | ${plan.target_date}</p>
        <small>${plan.created_at}</small>
      </div>
      <div class="saved-plan-actions">
        <button type="button" class="ghost-button load-plan">Load</button>
        <button type="button" class="ghost-button pdf-plan">PDF</button>
      </div>
    `;

    card.querySelector(".load-plan").addEventListener("click", async () => {
      const response = await fetch(`/api/plans/${plan.id}`);
      if (response.status === 401) {
        window.location.href = "/login";
        return;
      }
      if (!response.ok) return;
      const detail = await response.json();
      currentPayload = detail.payload;
      populateForm(detail.payload);
      renderStrategy(detail.strategy);
    });

    card.querySelector(".pdf-plan").addEventListener("click", () => {
      window.open(`/api/plans/${plan.id}/pdf`, "_blank");
    });

    savedPlansNode.appendChild(card);
  });
};

const refreshSavedPlans = async () => {
  const response = await fetch("/api/plans");
  if (response.status === 401) {
    window.location.href = "/login";
    return;
  }
  if (!response.ok) {
    savedPlansNode.className = "saved-plans empty-state";
    savedPlansNode.textContent = "Unable to load saved plans right now.";
    return;
  }
  renderSavedPlans(await response.json());
};

plannerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Generating strategy...", "loading");
  currentPayload = buildPayload();

  try {
    const result = await postJson("/api/generate-strategy", currentPayload);
    if (result) renderStrategy(result);
  } catch (error) {
    setStatus("Generation failed", "error");
    summaryNode.textContent = error.message;
    renderList(nextStepsNode, []);
    renderList(weeklyPlanNode, []);
    renderList(riskAlertsNode, []);
    renderChips([]);
  }
});

logoutButton.addEventListener("click", async () => {
  await postJson("/api/auth/logout", {});
  window.location.href = "/login";
});

savePlanButton.addEventListener("click", async () => {
  if (!currentPayload || !currentStrategy) {
    setStatus("Generate a strategy before saving.", "error");
    return;
  }

  const title = window.prompt("Plan title", `${currentPayload.exam_name} strategy`);
  if (!title) return;

  try {
    await postJson("/api/plans", {
      title,
      payload: currentPayload,
      strategy: currentStrategy,
    });
    await refreshSavedPlans();
    authStatus.textContent = "Plan saved";
    authStatus.dataset.variant = "success";
  } catch (error) {
    setStatus(error.message, "error");
  }
});

exportCurrentPdfButton.addEventListener("click", async () => {
  if (!currentPayload || !currentStrategy) {
    setStatus("Generate a strategy before exporting.", "error");
    return;
  }

  const title = `${currentPayload.exam_name} strategy`;
  const response = await fetch("/api/export-pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, payload: currentPayload, strategy: currentStrategy }),
  });

  if (!response.ok) {
    setStatus("Unable to export PDF right now.", "error");
    return;
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${title.toLowerCase().replace(/\s+/g, "-")}.pdf`;
  link.click();
  window.URL.revokeObjectURL(url);
});

addSubjectButton.addEventListener("click", () => {
  subjectsRoot.appendChild(subjectCard());
  renderPlannerVisual(buildPreviewPayload(), currentStrategy);
});

resetDemoButton.addEventListener("click", () => {
  plannerForm.reset();
  setDefaultDate();
  seedSubjects();
  currentPayload = null;
  currentStrategy = null;
  renderPlannerVisual();
  setStatus("Waiting for inputs");
  summaryNode.textContent = "Submit the form to generate a personalized strategy.";
  renderList(nextStepsNode, []);
  renderList(weeklyPlanNode, []);
  renderList(riskAlertsNode, []);
  renderChips([]);
});

plannerForm.addEventListener("input", () => {
  renderPlannerVisual(buildPreviewPayload(), currentStrategy);
});

plannerForm.addEventListener("change", () => {
  renderPlannerVisual(buildPreviewPayload(), currentStrategy);
});

setDefaultDate();
seedSubjects();
renderPlannerVisual(buildPreviewPayload(), null);
refreshSavedPlans();
