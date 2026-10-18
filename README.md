# Portfolio

Framework-free multi-page portfolio: HTML, CSS and JavaScript with native view transitions. No build step.

## Pages
- `index.html` — welcome and the claim-check illustration
- `projects.html` — project index with working deployment-state filters
- `contact.html` — contact buttons (addresses are assembled in `app.js`, not written in the HTML)
- `engineering.html`, `about.html`, `resume.html` — journal foundation, direction, factual summary
- `nexus-core.html`, `ella.html` — case studies with conceptual, clearly labeled architecture views
- `carecore.html`, `atelier.html`, `engine.html`, `ultimate-agentic-ai.html`, `lagoon.html`, `aurora.html` — short, evidence-labeled project pages
- `404.html`, `favicon.svg`

## Edit content
Project text, deployment states and links live in `data.js`. Contact details live in `app.js`. Icons are Simple Icons and Material Design Icons paths inlined as SVG.

## Run locally
Open `index.html`, or run `python3 -m http.server` and visit http://localhost:8000.

## Deploy
Any static host works. On Vercel, import the repo with no framework preset and no build command.
