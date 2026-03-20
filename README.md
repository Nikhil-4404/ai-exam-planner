# 🎓 Exam Preparation Strategy Planner

![React](https://img.shields.io/badge/React-19-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue.svg)
![Vite](https://img.shields.io/badge/Vite-8-purple.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

A production-ready, highly interactive web application designed to help students build structured, data-driven exam study plans. Whether you're preparing for JEE, UPSC, SATs, or any major certification, this planner helps you define your target, rank subjects by urgency, track milestones, and turn your available study time into highly focused, weekly execution sprints.

## 🚀 Features

- **🎯 Smart Exam Profiling**: Define your exam target date, allocate weekly study hours, set a goal score, and choose your preferred study style (Balanced, Concept-first, Practice-heavy).
- **📊 Subject Priority Engine**: Automatically ranks your subjects by urgency using an algorithm based on the gap between your current level and target level, syllabus coverage, and mock test scores. 
- **🗓️ Weekly Sprint Planning**: Intelligently converts your weekly hours into repeatable foundation, practice, and revision blocks with clear strategic intent.
- **✅ Milestone Tracking**: Keep your syllabus progression, mock test cycles, and revision runways visible by managing key milestones and deadlines.
- **💾 Auto-Persistence**: Automatically saves your strategy in local browser storage—no sign-up required.
- **📥 Exportable Strategy Brief**: Generates an exportable plain-text snapshot of your strategy for printing or sharing with mentors.

## 🛠️ Tech Stack

- **Frontend Framework**: [React 19](https://react.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Build Tool**: [Vite 8](https://vitejs.dev/)
- **Styling**: Vanilla CSS with customized design tokens

## 💻 Local Development

Follow these steps to get the project running on your local machine:

1. **Install dependencies**
   ```bash
   npm install
   ```
2. **Start the development server**
   ```bash
   npm run dev
   ```
   The dev server will be available at `http://localhost:5173`.

## 🚢 Deployment

The project is optimized for static deployment on platforms like Vercel, Netlify, or AWS Amplify.

### Vercel
1. Import the project into Vercel.
2. Vercel automatically detects Vite configurations. The build command `npm run build` and output directory `dist` will be selected automatically.
3. The included `vercel.json` already handles Single Page Application (SPA) routing rewrites.

### Netlify
1. Set the build command to `npm run build`.
2. Set the publish directory to `dist`.
3. Add a `_redirects` file in the `public` directory if you need fallback SPA routing:
   ```text
   /* /index.html 200
   ```

## 📂 Project Structure

```text
├── src/
│   ├── App.tsx      # Main planner logic, state management, and UI
│   ├── App.css      # Component-level layout styling
│   └── index.css    # Global styles, variables, and theme tokens
├── public/          # Static assets
└── package.json     # Project dependencies and bash scripts
```

## 📝 Notes & Usage Tips

- **Demo Data**: The application loads with default demo data. You can clear this easily by clicking "Reset demo data".
- **Coach View**: If your stress is too high or your study hours are too low for your target score, the app will generate actionable risk flags in the Coach View.
- **Offline Capable**: Since the data resides entirely within your device's `localStorage`, you can operate the planner offline once loaded.
