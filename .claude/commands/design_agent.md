# design-agent Command

Generate detailed Agent design documentation and implementation plan based on high-level design specifications.

## Objectives

1. Read high-level design document: `$ARGUMENTS`
2. Reference ADK development guide: https://github.com/Jiangwlee/claude_docs/blob/main/development-guild/adk_development_guide.md
3. Generate design documents in the same directory as the input specification

## Execution Steps

### 1. Understand The Project
- Start from CLAUDE.md to understand the current project

### 2. Analyze Input
- Read and parse the high-level design document content
- Extract project name, functional requirements, and technical specifications

### 3. Fetch Standards
- Retrieve and analyze the ADK development guide
- Extract key architectural patterns and best practices
- Identify applicable ADK components and tools

### 4. Design and Generate Documentation

Act as a senior software engineer and architect. Apply software engineering best practices, SOLID principles, design patterns, and industry standards to create comprehensive, production-ready detailed designs. Think systematically about scalability, maintainability, testability, and extensibility while considering real-world constraints and trade-offs.

Finally, create the following files:

**detailed_design.md**
- Project overview and architecture type
- Directory structure design
- Core module code frameworks
- Primary business flows
- Deployment strategies

**plan.md**
- Development task checklist ordered by dependencies
- Specific checkpoints for each task
- Risk assessment and milestones

## Output Requirements

- Generate all documentation in idiomatic, precise, and technically accurate English
- Provide executable code examples with comprehensive comments
- Follow ADK best practices and industry standards
- Consider real-world development scenarios and production requirements