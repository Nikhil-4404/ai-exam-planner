# Exam Preparation Strategy Planner

A production-ready React + TypeScript + Vite project for building structured exam study plans. The app helps students define an exam target, rank subjects by urgency, track milestones, and convert available study time into focused weekly sprints.

## Features

- Responsive dashboard with a polished planning-first interface
- Exam profile setup with target date, weekly hours, score goal, and study style
- Subject prioritization engine based on readiness, coverage, and mock performance
- Weekly sprint planning for foundation, practice, and revision work
- Milestone tracking for syllabus completion and mock cycles
- Local persistence using browser storage
- Exportable text strategy brief for sharing or printing
- Static deployment friendly output for Vercel, Netlify, or any Vite-compatible host

## Tech Stack

- React 19
- TypeScript
- Vite 8
- ESLint 9

## Local Development

```bash
npm install
npm run dev
```

The dev server will start on the local Vite default port.

## Production Checks

```bash
npm run lint
npm run build
```

Or run both together:

```bash
npm run check
```

## Deployment

### Vercel

1. Import the project.
2. Use the default Vite build command: `npm run build`.
3. Use `dist` as the output directory.
4. The included `vercel.json` handles SPA rewrites.

### Netlify

1. Build command: `npm run build`
2. Publish directory: `dist`

If you need SPA fallback on Netlify, add a `_redirects` file with:

```text
/* /index.html 200
```

## Project Structure

```text
src/
  App.tsx      Main planner logic and UI
  App.css      Component-level styles
  index.css    Global styles and theme tokens
public/
  site.webmanifest
```

## Notes

- Planner data persists in `localStorage`.
- The default data is demo content and can be reset from the UI.
- The generated export is a plain text study brief.
