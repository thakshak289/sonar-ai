# Sonar Sentinel

Build a polished SIH hackathon prototype web app called SONAR-AI — Intelligent Marine Debris Detection & Geospatial Analysis.

Context: This is an underwater side-scan sonar computer vision prototype. The current real AI model is GhostVision YOLO26 exported to ONNX and detects one current class, Crab-Pot, from sonar imagery. Do NOT claim it detects all marine debris. Use wording such as “Current AI prototype: derelict fishing-gear detection from side-scan sonar imagery.” The product vision is broader marine-debris detection.

IMPORTANT PRODUCT REQUIREMENT:
The app must accept BOTH a single sonar image and a complete sonar log. A user uploading a JPG/PNG/TIFF should get an immediate real detection workflow. The UI should also support XTF/JSF log upload as the mission-level workflow, but if the actual log parser/backend is not connected yet, clearly label log processing as “Prototype / Integration Ready” or “Coming next” rather than faking processing. Never invent real GPS coordinates. Demo map locations must be explicitly labeled simulated/demo if used.

Build the frontend as a professional dark ocean-tech dashboard using React/TypeScript, Tailwind and shadcn/ui. Make it look like an intermediate/student SIH team built a strong practical product — polished and modern, but not an over-designed commercial SaaS.

PAGES/SECTIONS:
1. Landing/dashboard page with SONAR-AI logo/text, short tagline, status indicator “AI Engine Online”, and two primary actions: “Analyze Sonar Image” and “Analyze Sonar Log”.
2. Image analysis workspace: large drag-and-drop upload area accepting JPG, PNG, TIFF; preview the uploaded sonar image; analyze button; loading/progress state; results view with annotated image, number of targets, high-risk count, average confidence, processing time, and a target list.
3. Detection result cards: class “Crab-Pot”, confidence percentage, risk badge. Risk can be presented as prototype confidence-based risk, not a scientifically validated risk model.
4. Mission Analysis section for XTF/JSF upload: explain the intended pipeline “Sonar Log → Ping/Navigation Extraction → Frame Generation → Preprocessing → YOLO26 Detection → Target Validation → Geolocation → Mission Report”. Make it obvious that full log integration is the next backend step.
5. Mission dashboard/map placeholder with a clean sonar survey map visual. If showing target markers without real nav data, label them “DEMO / SIMULATED LOCATION”.
6. Reports section placeholder showing the intended mission report fields: survey summary, detected targets, confidence/risk, coordinates when available, and export report.

DESIGN:
- Dark navy/charcoal background, subtle cyan/teal accents, white text, restrained green for positive status and amber/red for risk.
- Technical but clean typography.
- Sidebar navigation on desktop; responsive mobile layout.
- Top bar with system status and “Demo Mission” control.
- Use cards with subtle borders, not excessive gradients.
- Include a sonar-style circular/radar visual element in the dashboard header, but keep it tasteful.
- Use lucide icons.
- Add empty states and error states.
- Make upload interactions obvious and friendly.

DEMO MODE:
Include a “Launch Demo Mission” action that can use bundled/static sample sonar imagery if available later. For now build the UI/state architecture so demo data can be plugged in without changing the page design. Do not fabricate model detections; detection results should be marked demo/simulated unless returned by the backend.

BACKEND CONTRACT:
Prepare the frontend to call a FastAPI backend at an environment-configurable URL, defaulting to http://127.0.0.1:8000 during local development. Image endpoint: POST /api/analyze/image with multipart field `file`. Expected response shape: {success, filename, image:{width,height}, detections:[{label,confidence,risk,box:[x1,y1,x2,y2]}], summary:{total_targets,high_risk_targets,processing_time}, annotated_image}. Render returned annotated_image correctly, including absolute or relative backend URLs. Handle errors and backend-unavailable state gracefully.

Do not build fake AI logic in the frontend. The frontend must consume actual backend results when available. Make the code clean and componentized, and leave the app ready for deployment.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/db04cf4e-edea-4c2e-8052-437f9ab88c31).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
