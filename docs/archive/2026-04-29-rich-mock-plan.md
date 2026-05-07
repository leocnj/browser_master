# Implementation Plan: Rich Mock HR Interface (feat/rich_mock)

## Task 1: Update Backend Database and Endpoints
**File:** `mock-app/backend/server.js`
- **Action**: Modify the SQLite table creation to include `name`, `ssn`, `gender`, `salary`, `dental_plan`, `vision_plan`, and `medical_plan`.
- **Action**: Seed the database with 2-3 realistic mock employees (e.g., ID 123, 456).
- **Action**: Update the `POST /api/employee/:id/benefits` endpoint to accept updates for all three benefit types.

## Task 2: Define Premium Global Styles
**File:** `mock-app/frontend/src/styles.css`
- **Action**: Import a modern font (e.g., Inter from Google Fonts).
- **Action**: Define CSS variables for a premium dark/light mode palette (deep slate backgrounds, vibrant accent colors for buttons).
- **Action**: Create generic utility classes for glassmorphism panels, soft box shadows, and smooth transition animations (e.g., hover scaling for interactive elements).

## Task 3: Update Employee Component Logic
**File:** `mock-app/frontend/src/app/employee/employee.component.ts`
- **Action**: Update the component state variables to handle the expanded `employeeData` payload.
- **Action**: Add variables for editing `newDental`, `newVision`, and `newMedical` plans.
- **Action**: Update the `update()` fetch call to send the combined benefits payload.

## Task 4: Rebuild Template with Mixed Semantics & Aesthetics
**File:** `mock-app/frontend/src/app/employee/employee.component.html`
- **Action**: Wrap the entire application in a modern, centered layout.
- **Action**: Create a sleek "Search" header.
- **Action**: **Semantic Implementation**: Build the "Basic Info" section where Name and Gender have explicit `<label>` tags and properly associated `<input>` or `<select>` elements.
- **Action**: **Hostile DOM Implementation**: Build the "Confidential Info" (SSN, Salary) and "Benefits" (Dental, Vision, Medical) sections using heavily nested `<div>`s, generic `<span>` text, and inputs lacking IDs or names, relying instead on `ng-reflect` or positional context.

## Task 5: Review and Restart
- **Action**: Restart both the Express backend and Angular frontend servers.
- **Action**: Manually verify the premium aesthetics and functionality in the browser.
