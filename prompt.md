# Prompt 1 — Design & Plan

I teach OOP with Python at a university. I need to create a **complete, runnable Flask project** that my students will clone from GitHub. Before writing any code, I need you to **design and plan** the entire project.

## Concept

Students only write **pure Python code** — they never touch HTML, CSS, JS, or Flask routes. Everything else (frontend, routes, templates) is pre-built. Students implement Python classes/functions in designated files, and the frontend visually reflects their work. This makes OOP feel real — they see their code affect a UI.

## Student Background

**First semester (completed):** variables, types, operators, control flow, functions, lists, tuples, strings, regex, dictionaries, exception handling, file I/O, modules/APIs (`requests`), sets, comprehensions, `lambda`/`map`, `enumerate`/`zip`.

**Second semester (OOP, current):** classes, `__init__`, `self`, instance/class vars, encapsulation, `@property`, magic methods (`__str__`, `__add__`, `__eq__`, comparison operators), inheritance, composition, `super()`, polymorphism, ABC, duck typing, `@staticmethod`, `@classmethod`, decorators, dataclasses, type hints.

**Students do NOT know:** Flask, HTML, CSS, JavaScript, databases, REST APIs, async, or any web concepts.

## Syllabus


| Week   | Class Type  | Topic                                                                                                                                                                           |
| :----- | :---------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1**  | **Lecture** | **Classes and Objects**<br>- Transitioning from Procedural to OOP<br>- The `class` keyword and `__init__`<br>- Understanding `self`<br>- Instance Variables vs. Class Variables |
| **2**  | **Lecture** | **Encapsulation & Access Control**<br>- Public, Protected (`_`), and Private (`__`) attributes<br>- The Pythonic way: `@property` decorator<br>- Validation using setters       |
| **3**  | **Lecture** | **Magic Methods (Operator Overloading)**<br>- `__str__` vs `__repr__`<br>- Arithmetic: `__add__`, `__eq__`<br>- Making objects behave like built-in types                       |
| **4**  | **Lecture** | **Inheritance & Composition**<br>- "Is-A" (Inheritance) vs "Has-A" (Composition)<br>- `super()` and overriding<br>- Method Resolution Order (MRO)                               |
| **5**  | **Lecture** | **Polymorphism & Abstraction**<br>- Duck Typing<br>- Abstract Base Classes (`abc`)<br>- Defining Interfaces                                                                     |
| **6**  | **Lecture** | **Advanced Class Mechanics: Decorators**<br>- Writing custom Decorators<br>- `@staticmethod` vs `@classmethod`<br>- Factory pattern lite                                        |
| **7**  |             | **Revision Week**                                                                                                                                                               |
| **8**  |             | **Mid-term Exam**                                                                                                                                                               |
| **9**  | **Lecture** | **Modern Python Data Objects**<br>- `dataclasses` (Modern replacement for NamedTuples)<br>- Type Hinting basics                                                                 |
| **10** | **Lecture** | **Robust OOP: Exception Handling**<br>- Custom Exceptions<br>- Raising exceptions in Classes<br>- EAFP style                                                                    |
| **11** | **Lecture** | **Iterators, Generators & Context Managers**<br>- Iterator Protocol (`__iter__`)<br>- Generators (`yield`)<br>- Context Managers (`with`)                                       |
| **12** | **Lecture** | **Unit Testing & TDD**<br>- `pytest`: fixtures, parametrize, assertions<br>- Writing testable classes<br>- Brief intro to mocking                                               |
| **13** | **Lecture** | **SOLID Principles**<br>- Single Responsibility & Open/Closed<br>- Liskov Substitution & Interface Segregation<br>- Dependency Inversion<br>- Refactoring bad code examples     |
| **14** | **Lecture** | **Design Patterns**<br>- Singleton, Factory, Observer, Strategy<br>- When to use each pattern<br>- Real-world examples                                                          |
| **15** |             | Revision sessions                                                                                                                                                               |
| **16** |             | **Final Exam**                                                                                                                                                                  |


## This Week

- **Week:** 13
- **Topic:** **SOLID Principles**
- **Lecture material:** @lecture - read it fully

## What I Need From You

Design the project — **no code yet**. Create two files:

### 1. `plan.md`

Create a `plan.md` file in the project folder containing:

#### App Scenario
- A real-world app idea that feels like something students could imagine actually using — NOT a homework assignment.
- One-paragraph engaging description.

#### File & Folder Structure
- Full project tree.
- Use natural, real-world file and folder names (e.g., `models.py`, `services.py`, `validators.py` — whatever fits the scenario).
- Do NOT create an artificial `student_code/` folder or use names like `task1.py`.
- Students modify real application files that happen to start empty.

### 2. `README.md`

Create a `README.md` file in the project folder with the app description, setup instructions, and **6 progressive tasks**.

#### Task Difficulty Levels

Design **6 tasks** that gradually increase in difficulty from easy to advanced. Early tasks should be approachable for all students; later tasks should challenge even strong students. Use your judgment to decide what complexity is appropriate at each level based on the week's topic and previously covered material.

Tasks should be **progressive** — later tasks can build on earlier ones.

#### Mixing Topics (Critical)

Do NOT make every task only about this week's topic. Use this distribution:

- **Tasks 1–2:** Focus on **this week's topic only** — straightforward exercises to learn the new concept.
- **Tasks 3–6:** Combine **this week's topic with previous weeks' topics** (refer to the syllabus for what was covered in earlier weeks). These tasks should require students to integrate the new concept with things they've already learned.

This ensures students continuously practice what they've already learned, not just the latest topic.

#### Solution Length

Each task must require a **substantial implementation** — not a quick one-liner or a 5-line class. Aim for solutions that are roughly:

- **Easy tasks:** ~20–40 lines of Python
- **Medium tasks:** ~30–60 lines of Python
- **Hard tasks:** ~50–100+ lines of Python

To achieve this, design tasks that require multiple methods, attributes, validation logic, data processing, or interactions between objects. A task like "create a class with `__init__` and `__str__`" is too small — instead, require a class with several methods that do real work (filtering, calculating, transforming data, etc.).

#### Task Descriptions

Each task description must be **detailed enough that students can solve it independently** — specify what classes, methods, attributes, and behaviors are expected. For medium+ tasks, describe the **goal and requirements** but do NOT provide step-by-step instructions — let students figure out the implementation approach.

Use this format:

```markdown
# [Project Name]

[One-paragraph scenario description — make it engaging]

## Setup

\`\`\`bash
git clone [REPO_URL]
cd [PROJECT_NAME]
pip install -r requirements.txt
python app.py
\`\`\`

Open http://localhost:5000 in your browser.

## How This Works

- You ONLY modify Python files listed in the tasks below
- Do NOT touch any other files
- After making changes, restart the app (`Ctrl+C`, then `python app.py` again) and refresh the browser

## Tasks

### Task 1 (Easy): [Title]
**File:** `[path/to/file.py]`

[Description — NOT step-by-step hand-holding for medium+ and above]

**Verify:** [What to look for in the browser]

---

[...repeat for all 6 tasks...]
```

## Rules

- Do NOT create any code files yet — only `plan.md` and `README.md`.
- The scenario should feel like a real app.
- All student-facing instructions should be beginner-friendly (they don't know web development).
- Student files should start **blank** — no stubs, no boilerplate.

---

# Prompt 2 — Backend Scaffold

I'm building a Flask project for my OOP course. In the previous step, I designed the full plan.

Read `plan.md` and `README.md` in the project folder to understand the project design.

Now create all the **backend files** directly in the project folder:

1. **`app.py`** — Flask application with all routes
2. **All Python files** that are NOT student files (helpers, utilities, config, etc.)
3. **Empty student files** — completely blank `.py` files that students will implement
4. **`requirements.txt`**

## Rules

### Routes / app.py
- Flask routes should import from student files and handle `ImportError` or `AttributeError` gracefully.
- If student code isn't implemented yet, routes return sensible defaults so the app doesn't crash.
- Include helpful error messages in the terminal when student code is missing.
- Keep Flask code minimal and clean — it's scaffolding, not the focus.

### Student Files
- Must start **completely blank** — no stubs, no boilerplate, no comments.

### General
- The project should work on Python 3.10+.
- Do NOT create any frontend files (HTML, CSS, JS) — those come in the next step.
- Create every file with complete content — do not skip, summarize, or leave placeholders.

---

# Prompt 3 — Frontend

I'm building a Flask project for my OOP course. I've already designed the plan and built the backend.

Read `plan.md`, `README.md`, `app.py`, and all other Python files in the project folder to understand the design and backend structure.

Now create a plan to implement frontend: HTML templates, CSS, and JavaScript.

## Requirements

### UI Design
- The UI should look and feel like a **real app** — not a task checklist.
- No "Task 1", "Task 2" labels in the UI. Just a normal application with features that progressively start working as students implement the code.

### Graceful Fallbacks
- When a feature is not yet implemented, the UI should show graceful fallback (empty states, disabled sections) — NOT crash.
- When student code works, the UI should visibly change (new data appears, forms work, etc.).

### Technical
- Use HTML + CSS + vanilla JS only (no frameworks).
- Templates must match the routes defined in `app.py` exactly.
- Create every file with complete content — do not skip, summarize, or leave placeholders.

only plan for now

---

# Prompt 4 — Review & Polish

I'm building a Flask project for my OOP course. Here is the complete project:

Read all project files (`plan.md`, `README.md`, all Python files, all templates, CSS, and JS) thoroughly.

Review the entire project for **consistency and correctness**:

1. **Routes ↔ Templates:** Do all routes render the correct templates? Do all template names match?
2. **Routes ↔ Student files:** Do route imports match the actual student file paths and expected class/function names from the plan?
3. **Fallbacks:** Will the app run without errors when all student files are blank?
4. **README accuracy:** Do file paths in the README match the actual project structure?
5. **Task progression:** Can tasks be completed in order without conflicts?
6. **UI ↔ Backend data:** Does the frontend correctly display/use the data returned by routes?

If you find any issues, fix them directly in the project files. If everything is consistent, confirm it and note any minor improvements.
