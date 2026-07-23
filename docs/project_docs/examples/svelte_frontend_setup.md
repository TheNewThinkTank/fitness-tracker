# Frontend setup

> The frontend is already scaffolded under `frontend/`. These instructions are
> for reference only — follow them if you need to recreate it from scratch.

The project uses **Svelte 5** with a Rollup bundler.

```bash
mkdir frontend && cd frontend

# Scaffold a new Vite + Svelte project (official Svelte 5 approach)
npm create vite@latest . -- --template svelte
npm install

# Verify Svelte version
npm list svelte

# Start dev server
npm run dev
```

> **Note:** The older `npx degit sveltejs/template` approach scaffolds a
> Svelte 3/4 Rollup template that is no longer maintained. Do not use it
> for new Svelte 5 projects.
