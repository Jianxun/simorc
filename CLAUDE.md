## Development Guidelines

### Core Principles
- Always use the project wide python venv
- Follow test-driven development (TDD) approach
- Aim for MVP implementation following architecture decisions
- Maintain cross-session continuity through context management

### Development Workflow

#### 1. Task Selection and Planning
- Start each session by reviewing the `context/todo.md` file
- Select a specific task from the Current Sprint section
- Break down complex tasks into smaller subtasks as needed

#### 2. Test-Driven Development Cycle
- Write tests first that define the expected behavior
- Implement the minimum code needed to pass tests
- Run tests to verify functionality
- Refactor while maintaining test coverage

#### 3. Python-Specific Practices
- Follow PEP 8 style guidelines
- Use type hints to improve code readability and IDE support
- Organize imports alphabetically with standard library first
- Prefer explicit over implicit code
- Document functions and classes with docstrings

### Testing Organization
- Organize test files as `test_*.py` in the `/tests/` directory
- Use pytest for test execution and assertions
- For complex components, create subdirectories: `/tests/{component}/`
- Save test fixtures in separate files or a fixtures directory

### Refactoring Guidelines
- Schedule regular refactoring sessions in the todo list
- Focus on one aspect per refactoring session (e.g., organization, performance)
- Maintain test coverage during refactoring
- Document architectural changes in `context/memory.md`

### When Tests Fail
- Troubleshoot and fix all errors and warnings
- Record challenging bugs and their solutions in `context/memory.md`

### When Tasks Are Completed
1. Update the todo list to mark task completion
2. Update the memory file to reflect current project state
3. Consider adding a new task for refactoring if appropriate
4. Commit changes with a descriptive message
5. End the session or move to the next task

## Context Management

This project uses a context directory to maintain continuity between chat sessions. The assistant should actively maintain these files throughout the project lifecycle.

### Context Structure

The context is stored in markdown files in the `context` directory:

```
context/
  ├── memory.md   # Project state, decisions, and knowledge
  └── todo.md     # Task tracking and completion status
```

### Setup

When first interacting with the project, the assistant should:

1. Check if the `context` directory exists; if not, suggest creating it
2. Check if required files exist; if not, suggest creating them with the templates below
3. Always review context files at the beginning of each session

### Memory File (memory.md)

Maintains the project's state, decisions, and knowledge.

#### Template

```markdown
# Project Memory

## Project Overview
[Brief description of the project]

## Current State
[Description of the current state of the project]

## Key Decisions
[List of key decisions made during the project]

## Open Questions
[List of open questions that need to be addressed]
```

#### Usage Guidelines

- Update after significant progress or decisions
- Include rationale for key decisions
- Record blockers and their resolutions
- Keep summary of current state accurate

### Todo List (todo.md)

Tracks tasks and completion status.

#### Template

```markdown
# Project Todo List

## Current Sprint
[List of tasks for the current sprint]

## Backlog
[List of tasks for future sprints]

## Completed Tasks
[List of completed tasks]
```

#### Usage Guidelines

- Mark tasks using checkboxes: `[ ]` for pending, `[X]` for completed
- Move completed tasks to the "Completed Tasks" section
- Prioritize tasks in the "Current Sprint" section
- Add any new requirements to the "Backlog" section
- Include sub-tasks with indentation where appropriate

### Maintenance Procedures

1. **Beginning of session**:
   - Review both context files to understand current state
   - Ask for updates if context appears outdated

2. **During session**:
   - Reference context when discussing tasks
   - Suggest changes to context files when new information emerges

3. **End of session**:
   - Update the memory file with new decisions or information
   - Update the todo list with new or completed tasks
   - Summarize changes made to context files

## Tools and Commands

- Use `waveview` command to inspect spice `.raw` files by running: `waveview signals filename.raw`, use `--help` option to learn about the tool.