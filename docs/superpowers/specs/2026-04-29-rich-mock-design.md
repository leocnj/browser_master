# Design Spec: Rich Mock HR Interface (feat/rich_mock)

## 1. Objective
Enhance the existing barebones mock HR application into a realistic, enterprise-grade simulation. The updated mock will feature a premium, dynamic UI, realistic employee data (SSN, Name, Gender, Salary, Benefits), and intentionally chaotic accessibility patterns typical of legacy enterprise applications.

## 2. Requirements & Scope
1.  **Extended Data Model**:
    *   Expand the SQLite backend to store: `id`, `name`, `ssn`, `gender`, `salary`, `dental_plan`, `vision_plan`, `medical_plan`.
    *   Seed the database with a few realistic employee profiles.
2.  **Mixed Accessibility (Hostile DOM)**:
    *   **Semantic**: Some inputs will use proper HTML5 semantics (e.g., `<label for="name">Name</label><input id="name">`).
    *   **Meaningless (Legacy)**: Key fields (like SSN, Salary, Benefits) will use meaningless `<div>` wrappers and `ng-reflect` attributes with no `id` or `<label>` tags, forcing the automation script to use complex fallback locators (XPath adjacent text, etc.).
3.  **Premium Aesthetics & UI**:
    *   Implement a high-end, modern design system using Vanilla CSS.
    *   Use a sleek, corporate dark/light palette with glassmorphism elements, subtle gradients, and soft shadows.
    *   Include micro-animations (e.g., hover states on buttons, smooth transitions for fetching employee data).
    *   Utilize modern typography (e.g., Inter or Roboto via Google Fonts).

## 3. Architecture & Components

### 3.1 Backend (`mock-app/backend/server.js`)
*   **Database Schema Update**: Recreate the `employees` table with the new fields.
*   **API Endpoints**:
    *   `GET /api/employee/:id`: Returns the full profile.
    *   `POST /api/employee/:id/benefits`: Updates the benefit choices (Dental, Vision, Medical).

### 3.2 Frontend (`mock-app/frontend/`)
*   **Styles (`styles.css` / `employee.component.css`)**: Define the global CSS variables, typography, and card-based layout system. Add hover effects for the "Search" and "Save" buttons.
*   **Template (`employee.component.html`)**:
    *   A sleek search bar component for the Employee ID.
    *   A "Profile Card" displaying Name, SSN, Gender, and Salary.
    *   An interactive "Benefits Enrollment" section with dropdowns/inputs for Medical, Dental, and Vision.
*   **Logic (`employee.component.ts`)**: Bind the new data model and update the `fetch` logic to handle the new endpoints.

## 4. Automation Impact
By mixing standard semantic HTML with legacy `<div>` structures, this "rich mock" will serve as the perfect testing ground for the `browser-use` Playwright generation tool, proving its ability to navigate a chaotic DOM while still successfully fulfilling user tasks.
