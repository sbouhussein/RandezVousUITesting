# Claude Code Guidelines: Test Automation

This document outlines the core commands, context management strategies, and best practices for using Claude Code to build and maintain our test suites. 

## Core Commands

* **`/clear`**: Wipes the current context window. 
  * *When to use:* Use this constantly when switching between different types of testing (e.g., moving from unit testing a Firebase Cloud Function to writing an E2E test for the React web app). It prevents the agent from hallucinating old mocks or assertions into your new tests and keeps token usage low.
* **`/undo`** *(or `/rewind`)*: Time-travel for your chat. 
  * *When to use:* If Claude starts generating overly complex custom mocks or goes down a rabbit hole trying to fix a flaky test in the wrong way, use this to revert to a clean state.
* **`/resume`**: Re-opens your last session. 
  * *When to use:* Great for picking right back up after clearing your terminal mid-test-run.

## Context Management (Speed & Limits)

* **Pass Targeted Context:** Don't let Claude read the whole repository. When asking for a test, pass the specific file being tested, its dependencies, and the test setup file. 
* **Cross-Platform Context:** Since our platform spans multiple environments, give Claude the specific, isolated context it needs:
  * *Backend/Database:* If you're testing Firebase security rules, pass the Firestore rules file and the specific test utility.
  * *iOS:* If you are writing UI tests, pass the relevant SwiftUI views and view models.
  * *Web/Cross-Platform:* If you are testing the map interface, pass the React components. If testing the Android Trusted Web Activity (TWA), pass the specific web components being wrapped.
* **Use a `.claudesignore` file:** Prevent Claude from reading heavy, irrelevant directories that eat up your context window, such as `node_modules.

## Mindset & Test Strategy

* **You Own the Test Strategy:** Claude is incredible at writing boilerplate, generating mock data, and writing out repetitive assertions. However, *you* are the expert on the product and what constitutes a valuable test. If Claude suggests testing implementation details rather than user behavior, reject it and guide it back.
* **The Default Model is Solid:** The default model provides the best balance of speed and reasoning for writing test scripts, resolving test failures, and debugging CI/CD pipelines.
* **Generate the Plan, Then the Code:** Instead of asking for "full coverage on this file," ask Claude to first outline the test cases it plans to write (happy path, edge cases, error states). Once you approve the list, ask it to generate the actual code.