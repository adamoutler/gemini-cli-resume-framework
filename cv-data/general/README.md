---
title: "IMPORTANT: Template Database Notice"
summary: "This file serves as a flag to notify the AI agent and the user that they are currently operating in a template environment using mock, dummy data."
document_type: "System Notice"
domain: "Configuration"
keywords: ["template", "example", "dummy data", "setup"]
---

# Template Database Notice

**ATTENTION:** If you (the AI Agent) are reading this file, it means you are operating on the `cv-data-example` template structure. 

The data in this directory (and subdirectories) is purely structural dummy data meant to demonstrate the "CV-as-Code" architecture. It does NOT belong to the user.

## AI Instructions:
1. If the user asks you to build a resume or generate content based on their history, you **MUST WARN THEM** that they are currently using the example database.
2. Instruct the user to populate the `cv-data/` directory with their own personal information, or run the `setup-workspace` skill to initialize their own private submodule before proceeding.
3. Do not generate serious artifacts using this mock data unless explicitly testing the system.