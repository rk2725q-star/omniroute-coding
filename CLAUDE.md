# User-Decided 5-in-1 Mega-Batch Architecture Protocol

## 🎯 CORE PRINCIPLE: USER-DRIVEN DECISIONS, AUTONOMOUS 1-PASS EXECUTION

The AI MUST NOT make arbitrary architectural or design decisions on behalf of the user. Architecture is executed in a structured 2-phase workflow:

---

### 📋 Phase 1: User Decision & Alignment (User in Full Control)
When the user requests a new feature or product:
1. **Present Key Architectural Options**:
   - Database / Schema choices (e.g., SQLite vs Postgres, data models).
   - Backend & Auth choices (e.g., JWT vs Session, API structure).
   - Frontend UI & Aesthetic choices (e.g., Dark Mode Glassmorphism vs Minimal Clean, layout style).
2. **Collect User Requirements**: Ask clarifying questions or present structured choices so the user decides exactly how the product should look and behave.
3. **Wait for User Decision**: Do not start writing partial code until the user confirms their preferred choices.

---

### 🚀 Phase 2: Single-Pass 5-in-1 Mega-Batch Build (Post-Confirmation)
Once the user confirms their decisions, execute the complete end-to-end system in **1 single execution turn with 1 streaming response**:

1. 🗄️ **Schema & Data Models**: Fully aligned with the user's chosen DB schema and types.
2. ⚙️ **Backend Logic & Route Handlers**: 100% complete business logic, validations, and API endpoints.
3. 🎨 **Frontend UI Components**: Interactive components built to the user's chosen UI specs and states.
4. 💅 **Production Styling & Micro-Animations**: Tailored styling matching the user's chosen visual aesthetic.
5. 🧪 **Automated Unit Tests & Verification**: Pass-verified unit/integration test scripts.

---

### Strict Quality Rules:
- **Zero Incomplete Stubs**: No `// TODO` or placeholder code.
- **Continuous 1-Turn Stream**: All 5 layers created in one uninterrupted batch once confirmed.
- **Maximum Quota Efficiency**: Zero wasted requests from unaligned guessing.
