# Memory Bank

This directory contains the project's Memory Bank - a comprehensive knowledge base that persists across AI sessions.

## Purpose

The Memory Bank serves as the single source of truth for project context, ensuring continuity and understanding across development sessions. It's designed to be read at the start of every task to provide complete project context.

## Structure

### Core Files (Required)

1. **projectbrief.md** - Foundation document
   - Core mission and objectives
   - Success criteria
   - Scope boundaries
   - Key decisions

2. **productContext.md** - Product understanding
   - Problem statement
   - User experience goals
   - User flows
   - Feature priorities

3. **systemPatterns.md** - Architecture and patterns
   - Design patterns in use
   - Component relationships
   - Data flow patterns
   - Code organization

4. **techContext.md** - Technical details
   - Technology stack
   - Dependencies
   - Configuration
   - Development environment

5. **activeContext.md** - Current state
   - Recent work focus
   - Active issues
   - Next steps
   - Recent decisions

6. **progress.md** - Status tracking
   - What works
   - What's left to build
   - Known issues
   - Completion status

## Usage

**For AI Assistants:**
- Read ALL memory bank files at the start of every task
- Update files when discovering new patterns or making significant changes
- Use as reference for project context and decisions

**For Developers:**
- Reference for project understanding
- Quick onboarding resource
- Decision history and rationale

## File Relationships

```
projectbrief.md (foundation)
    ↓
productContext.md + systemPatterns.md + techContext.md
    ↓
activeContext.md + progress.md (current state)
```

## Update Guidelines

- **After significant changes:** Update relevant files
- **When user requests:** Review and update ALL files
- **When patterns emerge:** Document in systemPatterns.md
- **When status changes:** Update activeContext.md and progress.md

---

**Last Updated:** November 2025

