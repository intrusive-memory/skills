# Military Operation Name Pattern Examples

## The Pattern

Transform a feature's core purpose into a vivid metaphor using concrete imagery. Make it slightly absurd but recognizable.

**Format**: `OPERATION [ADJECTIVE/ACTION] [CONCRETE NOUN]`

## Example Transformations

### Given by User
- **Speech synthesis** → **OPERATION SHOUTING MOON**
  - Speaking = shouting
  - Voice across space = moon
  - Evokes: Broadcasting sound into the void

### Software Development Examples

1. **User authentication system** → **OPERATION GATEKEEPER HANDSHAKE**
   - Verification = gatekeeper
   - Login = handshake
   - Evokes: Formal entry protocol

2. **Database migration** → **OPERATION MARCHING ELEPHANTS**
   - Moving data = marching
   - Large datasets = elephants
   - Evokes: Slow, deliberate, unstoppable progress

3. **PDF generation** → **OPERATION PAPER FOUNDRY**
   - Creating documents = foundry (manufacturing)
   - PDF = paper
   - Evokes: Industrial document production

4. **Real-time chat** → **OPERATION LIGHTNING TELEGRAPH**
   - Fast = lightning
   - Messaging = telegraph
   - Evokes: Instant communication across distance

5. **File compression** → **OPERATION STEAMROLLER ORIGAMI**
   - Applying pressure = steamroller
   - Reducing size = origami (folding)
   - Evokes: Forceful minimization

6. **API rate limiting** → **OPERATION TRAFFIC COP**
   - Controlling flow = traffic cop
   - Evokes: Order from chaos

7. **Image processing** → **OPERATION MIRROR POLISHER**
   - Transforming images = polishing mirrors
   - Evokes: Refinement and clarity

8. **Caching system** → **OPERATION SQUIRREL VAULT**
   - Storing = vault
   - Quick retrieval = squirrel (hoarding nuts)
   - Evokes: Strategic storage for later

9. **Encryption** → **OPERATION LOCKSMITH RIDDLE**
   - Securing = locksmith
   - Complex algorithm = riddle
   - Evokes: Deliberate obfuscation

10. **Background job queue** → **OPERATION NIGHT SHIFT**
    - Async/background = night shift
    - Evokes: Work happening while others sleep

11. **WebSocket server** → **OPERATION RADIO TOWER**
    - Broadcasting = radio tower
    - Persistent connection = tower (always there)
    - Evokes: Always-on communication hub

12. **Automated test suite** → **OPERATION SAFETY INSPECTOR**
    - Verification = inspector
    - Preventing bugs = safety
    - Evokes: Rigorous quality checks

13. **CI/CD pipeline** → **OPERATION ASSEMBLY LINE**
    - Automation = assembly line
    - Continuous = line (never stops)
    - Evokes: Efficient, repeatable process

14. **Code formatter** → **OPERATION BARBER SHOP**
    - Styling code = barber styling hair
    - Evokes: Making messy things neat

15. **Dependency injection** → **OPERATION SUPPLY DROP**
    - Providing dependencies = supply drop
    - Evokes: Delivering what's needed from above

16. **Logging system** → **OPERATION BLACK BOX**
    - Recording events = black box (flight recorder)
    - Evokes: Preserving history for investigation

17. **GraphQL API** → **OPERATION MENU PRINTER**
    - Flexible queries = ordering from menu
    - API responses = printed orders
    - Evokes: Custom service on demand

18. **OAuth flow** → **OPERATION BOUNCER BADGE**
    - Authorization = bouncer
    - Token = badge
    - Evokes: Proving you belong

19. **Error monitoring** → **OPERATION SMOKE ALARM**
    - Detecting errors = smoke alarm
    - Evokes: Early warning system

20. **Package manager** → **OPERATION WAREHOUSE FORKLIFT**
    - Managing dependencies = warehouse
    - Installing packages = forklift (moving goods)
    - Evokes: Organized distribution

## Derivation Rules for Haiku Agent

When generating an operation name from an execution plan:

1. **Extract core action** (1 sentence summary of what the plan does)
   - Example: "Adds voice synthesis to the audio library"

2. **Identify the metaphor**
   - What does this *feel* like?
   - What concrete, physical activity is analogous?
   - Speech synthesis → Broadcasting sound → Shouting into space

3. **Choose vivid imagery**
   - Use concrete nouns (MOON, ELEPHANT, TOWER, BARBER)
   - Use evocative actions/adjectives (SHOUTING, MARCHING, LIGHTNING)
   - Prefer absurd-but-apt combinations

4. **Combine into format**
   - OPERATION [ACTION/ADJECTIVE] [NOUN]
   - Must be 2-4 words after "OPERATION"
   - ALL CAPS

5. **Humor check**
   - Does it make you smile?
   - Is it slightly ridiculous but still recognizable?
   - Would a military person raise an eyebrow?

## Anti-Patterns (Avoid These)

❌ **Too literal**: "OPERATION ADD AUTHENTICATION" (boring, not evocative)
❌ **Too abstract**: "OPERATION PARADIGM SHIFT" (meaningless)
❌ **Too obscure**: "OPERATION QUANTUM FLUX" (nobody knows what this means)
❌ **Too serious**: "OPERATION SECURE LOGIN" (sounds real, not humorous)
❌ **Too long**: "OPERATION EXTREMELY LOUD AND INCREDIBLY CLOSE MESSAGING SYSTEM"

✅ **Just right**: "OPERATION GATEKEEPER HANDSHAKE" (evocative, absurd, recognizable)

## Usage in Sub-Skill

```markdown
## Generate Feature Name

You are using the **haiku** model (cheapest) for this task.

### Input
- Read EXECUTION_PLAN.md
- Extract the core purpose (what does this plan accomplish?)

### Process
1. Summarize the plan's actions in one sentence
2. Identify the core metaphor (what is this *like*?)
3. Choose vivid, concrete imagery
4. Combine into military operation format
5. Ensure it's humorous but recognizable

### Output
- Generate: `OPERATION [ACTION] [NOUN]` (ALL CAPS)
- Add to EXECUTION_PLAN.md frontmatter:
  ```yaml
  ---
  feature_name: OPERATION SHOUTING MOON
  ---
  ```

### Examples to Reference
[Include 5-10 examples from this document]
```

## Test Cases

Use these to validate the pattern:

| Input Feature | Expected Style | Sample Output |
|---------------|----------------|---------------|
| Add Spotify integration | Music + Connection | OPERATION JUKEBOX HANDSHAKE |
| Implement dark mode | Theme + Vision | OPERATION MOONLIGHT PAINTER |
| Build notification system | Alerts + Attention | OPERATION TOWN CRIER |
| Create admin dashboard | Overview + Control | OPERATION WATCHTOWER |
| Add multi-language support | Translation + Voice | OPERATION BABEL PARROT |
| Implement file upload | Transfer + Movement | OPERATION CARGO CRANE |
| Add search functionality | Discovery + Vision | OPERATION BLOODHOUND LENS |
| Create user onboarding | Introduction + Journey | OPERATION WELCOME WAGON |
| Implement data export | Extraction + Escape | OPERATION PRISON BREAK |
| Add keyboard shortcuts | Speed + Input | OPERATION LIGHTNING FINGERS |

The haiku agent should be able to generate similarly creative names when given a plan summary.
