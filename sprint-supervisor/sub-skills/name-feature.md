# Name Feature Sub-Skill

Part of the Sprint Supervisor skill. Generates humorous military operation names for execution plans.

**Model**: Use **haiku only** (cheapest, pattern-based generation)

**When called**:
1. Automatically by `start` command (THE RITUAL)
2. Manually by user to regenerate existing name

**Sacred Rule**: NAMING IS A RITUAL OF STARTING THE PLAN. Cannot name before execution begins.

---

## Startup Check

### Step 1: Determine Call Context

Check who called this sub-skill and what state exists:

**Context A: Called manually by user BEFORE any execution state**
- Check if `SUPERVISOR_STATE.md` exists in project root
- Check if `EXECUTION_PLAN.md` has frontmatter with `feature_name`
- If NEITHER exists → PREMATURE NAMING (deliver reproach)

**Context B: Called by `start` command**
- `start` command is initiating execution
- This is THE RITUAL (ceremonial announcement)

**Context C: Called manually AFTER execution started**
- `SUPERVISOR_STATE.md` exists OR `feature_name` frontmatter exists
- User wants to regenerate name (quiet confirmation)

### Step 2: Route to Appropriate Handler

- Context A → Jump to "Premature Naming Reproach" section
- Context B → Jump to "Generate Name (Ceremonial)" section
- Context C → Jump to "Generate Name (Regenerate)" section

---

## Premature Naming Reproach

User tried to name before starting. Educate them with personality.

```
Pfft... child! You want to name an operation before you're ready to launch it?

NAMING IS A RITUAL OF STARTING THE PLAN.

Here's the flow:
1. breakdown → creates the plan
2. analyze/evaluate/prioritize → refine the plan (optional)
3. start → THE RITUAL: generates your operation name and kicks off execution

Are you READY to start? Because if you call 'start', we're going live.
No turning back. The troops deploy. The code ships.

Otherwise, go back and refine your plan. When you're ready, say 'start'.

(If you've already started and want to change the name, that's fine.
 But you can't name something that doesn't exist yet. That's just silly.)
```

**Then STOP.** Do not proceed to name generation.

---

## Generate Name (Ceremonial)

Called by `start` command. This is THE RITUAL.

### Step 1: Read Execution Plan

Read `EXECUTION_PLAN.md`. Extract the core purpose of the plan.

### Step 2: Summarize Mission (haiku model)

Generate a one-sentence summary of what this plan accomplishes.

**Prompt for haiku**:
```
Read this execution plan and summarize its core purpose in one sentence.
Focus on the main deliverable or feature being built.

[Include EXECUTION_PLAN.md content]

Output format: One sentence, no preamble.
Example: "Add text-to-speech synthesis capabilities to the audio library"
```

### Step 3: Generate Operation Name (haiku model)

Transform the summary into a humorous military operation name.

**Prompt for haiku**:
```
Generate a humorous military operation name for this feature.

Feature summary: [one-sentence summary from Step 2]

Follow this pattern:
1. Extract the core action (what does this DO?)
2. Find a vivid metaphor (what is this LIKE in the physical world?)
3. Use concrete imagery (nouns like MOON, TOWER, ELEPHANT)
4. Combine as: OPERATION [ACTION/ADJECTIVE] [NOUN]
5. Make it slightly absurd but recognizable

Examples to guide your pattern:
- Speech synthesis → OPERATION SHOUTING MOON
- User authentication → OPERATION GATEKEEPER HANDSHAKE
- Database migration → OPERATION MARCHING ELEPHANTS
- PDF generation → OPERATION PAPER FOUNDRY
- Real-time chat → OPERATION LIGHTNING TELEGRAPH
- File compression → OPERATION STEAMROLLER ORIGAMI
- API rate limiting → OPERATION TRAFFIC COP
- Caching system → OPERATION SQUIRREL VAULT
- Encryption → OPERATION LOCKSMITH RIDDLE
- Background jobs → OPERATION NIGHT SHIFT

Output format: OPERATION [NAME] (ALL CAPS, 2-4 words after OPERATION)
```

**Validation**:
- Must start with "OPERATION "
- Must be ALL CAPS
- Must be 2-4 words after "OPERATION"
- Must be creative/humorous (not literal like "OPERATION ADD AUTHENTICATION")

If generated name fails validation, retry once with stronger guidance.

### Step 4: Add Frontmatter to EXECUTION_PLAN.md

Read current `EXECUTION_PLAN.md` content.

Check if frontmatter already exists:
- If yes: update `feature_name` field
- If no: insert frontmatter at top

**Frontmatter format**:
```yaml
---
feature_name: OPERATION [GENERATED NAME]
---
```

Write the updated file.

### Step 5: Display Ceremonial Announcement

Output the operation name with ceremony:

```
┌─────────────────────────────────────────────┐
│  🎖️  OPERATION [GENERATED NAME] 🎖️           │
│                                             │
│  Mission: [one-line summary]               │
│  Status: COMMENCING                        │
│  Sprints: [N] across [M] work units        │
└─────────────────────────────────────────────┘

Operation name logged in EXECUTION_PLAN.md frontmatter.

Ready to roll? Dispatching Sprint 1...
```

**Important**: The line "Ready to roll? Dispatching Sprint 1..." signals to the `start` command that naming is complete and execution should begin.

---

## Generate Name (Regenerate)

Called manually after execution already started. Quiet confirmation, no ceremony.

### Steps 1-4: Same as Ceremonial

Follow Steps 1-4 from "Generate Name (Ceremonial)" section.

### Step 5: Display Quiet Confirmation

Output a simple confirmation without the ceremony box:

```
Regenerating operation name...

Old: OPERATION [OLD NAME]
New: OPERATION [NEW NAME]

Updated EXECUTION_PLAN.md frontmatter.

(The new name will be used for archival when the mission completes)
```

---

## Error Handling

### EXECUTION_PLAN.md Not Found

```
Whoa there, soldier! Can't name an operation without a plan.

Run one of these first:
- /sprint-supervisor breakdown [requirements.md] (create a plan)
- Provide the plan path: /sprint-supervisor name-feature /path/to/EXECUTION_PLAN.md
```

### Empty or Invalid Plan

```
This execution plan is empty or malformed.

Fix the plan structure, then try again.
```

### Name Generation Failed (haiku didn't follow pattern)

Retry once with stronger guidance. If still fails:

```
Operation name generation struggled (AI creativity malfunction).

Falling back to: OPERATION [PROJECT_DIR_NAME]

(You can manually edit EXECUTION_PLAN.md frontmatter to change it)
```

---

## Integration Notes

**When `start` calls this sub-skill**:
1. `start` detects missing `feature_name` frontmatter
2. `start` invokes name-feature logic (Context B)
3. name-feature generates name, displays ceremony
4. name-feature outputs "Ready to roll? Dispatching Sprint 1..."
5. `start` continues with sprint dispatch

**When user calls manually**:
1. User runs `/sprint-supervisor name-feature`
2. Check context (A, B, or C)
3. Route to appropriate handler
4. If Context A: reproach and stop
5. If Context C: regenerate and confirm

---

## Personality Notes

- **Reproach**: Playful, not mean. Educate the user about the ritual.
- **Ceremony**: Make it feel significant. The box, the emoji, the phrasing.
- **Regenerate**: Low-key. They already know the ritual, just changing the name.

---

## Model Usage

**ALL name generation uses haiku**:
- Summarizing mission: haiku
- Generating operation name: haiku
- No sonnet or opus needed (pattern-based, not complex reasoning)

**Cost optimization**: haiku is 1x cost, sonnet is 10x, opus is 30x. Naming is a simple task, so haiku is perfect.
