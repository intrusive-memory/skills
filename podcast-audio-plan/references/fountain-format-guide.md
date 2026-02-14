# Fountain Format Guide for Podcasts

Quick reference for writing Fountain screenplay files optimized for podcast audio generation with Produciesta.

## What is Fountain?

Fountain is a simple markup syntax for writing screenplays in plain text. It's designed to be readable in any text editor while being parsable by software.

**Official spec**: https://fountain.io/

## Basic Elements

### Scene Headings

Scene headings establish location and time of day.

```fountain
INT. COFFEE SHOP - DAY

EXT. PARK - NIGHT

INT./EXT. CAR - CONTINUOUS
```

**For podcasts**: Scene headings can be spoken by a narrator or omitted entirely.

### Action

Action describes what happens. Written in plain text.

```fountain
Alice walks into the coffee shop and orders a latte.

The barista nods and starts preparing the drink.
```

**For podcasts**: Action is typically spoken by a narrator character.

### Dialogue

Character name in ALL CAPS, followed by dialogue on the next line.

```fountain
ALICE
I'll have a large latte, please.

BARISTA
Coming right up!
```

**For podcasts**: This is the core content. Each character needs a voice assigned in PROJECT.md.

### Character Names

Character names must be ALL CAPS and on their own line.

```fountain
NARRATOR
Welcome to today's episode.

ALICE
Hello!

BOB
Hi there!
```

**Character variations**: All map to the same character in cast list:
- `BOB`
- `BOB (V.O.)` - Voice over
- `BOB (O.S.)` - Off screen
- `BOB (CONT'D)` - Continued

### Parentheticals

Character direction in parentheses.

```fountain
ALICE
(whispering)
Did you hear that?

BOB
(shouting)
What?!
```

**For podcasts**: Parentheticals are NOT spoken - they're director notes. Use them to indicate tone, but the actual text won't be in the audio.

### Lyrics

Use `~` to indicate singing.

```fountain
SINGER
~Happy birthday to you~
~Happy birthday to you~
```

**For podcasts**: Produciesta automatically uses appropriate intonation for lyrics.

### Dual Dialogue

Use `^` after character name for simultaneous speech.

```fountain
ALICE ^
I think we should go left.

BOB ^
I think we should go right.
```

**For podcasts**: Both characters speak at the same time (overlapping audio).

### Transitions

```fountain
FADE IN:

CUT TO:

FADE OUT.
```

**For podcasts**: Transitions can be spoken by narrator or omitted.

## Advanced Features

### Centered Text

Use `>` and `<` to center text.

```fountain
> THE END <
```

### Page Breaks

Use `===` for page breaks (ignored in audio).

```fountain
===
```

### Sections and Synopses

Use `#` for sections (organizational, not spoken).

```fountain
# Act One

## Scene 1

= Alice meets Bob at the coffee shop
```

### Notes

Use `[[` and `]]` for production notes (not spoken).

```fountain
ALICE
I can't believe this! [[emphasize disbelief]]
```

### Boneyard

Comment out sections with `/*` and `*/`.

```fountain
/*
ALICE
This line won't be in the final script.
*/
```

## Podcast-Specific Best Practices

### 1. Always Use a Narrator

For scene headings and action:

```fountain
NARRATOR
Interior, coffee shop, morning. Alice enters and approaches the counter.

ALICE
One coffee, please.
```

### 2. Minimize Parentheticals

Since they're not spoken, use them sparingly:

```fountain
ALICE
(whispering)
This works - spoken as whisper.

ALICE
(looks around nervously)
This doesn't - "looks around" isn't spoken.
```

### 3. Character Name Consistency

Use the same name format throughout:

```fountain
ALICE
Hello!

ALICE
How are you?
```

Not:

```fountain
ALICE
Hello!

Alice
How are you?  # Wrong - lowercase won't be recognized as dialogue
```

### 4. Text Filtering Syntax

Use `{{...}}` to mark text that should NOT be spoken:

```fountain
ALICE
Hello {{stage whisper}} world!
```

**Result**: Speaks "Hello world!" (filters out "stage whisper")

### 5. Avoid Excessive Action

Keep action blocks concise for narrator:

```fountain
NARRATOR
Alice walks to the door. She opens it. She enters the room. She closes the door behind her.
```

Better:

```fountain
NARRATOR
Alice enters the room and closes the door behind her.
```

## Character Naming Conventions

### Normalized Names

Produciesta normalizes character names:

```fountain
BOB
Hello!

BOB (V.O.)
Hello again!

BOB (O.S.)
One more time!
```

All three map to the same `BOB` character in PROJECT.md cast list.

### Multiple Characters

For ensemble casts:

```fountain
NARRATOR
Chapter one begins.

ALICE
I'm Alice.

BOB
I'm Bob.

CHARLIE
And I'm Charlie.
```

Each needs a voice in PROJECT.md:

```yaml
cast:
  - character: NARRATOR
    voices:
      - apple://com.apple.voice.premium.en-US.Aaron
  - character: ALICE
    voices:
      - apple://com.apple.voice.premium.en-US.Ava
  - character: BOB
    voices:
      - apple://com.apple.voice.premium.en-US.Daniel
  - character: CHARLIE
    voices:
      - apple://com.apple.voice.premium.en-US.Fred
```

## Complete Example

```fountain
Title: The Daily Dao - Chapter 01
Credit: Written by
Author: Tom Stovall
Draft date: 2026-02-11

FADE IN:

NARRATOR
Chapter one. The Tao that can be told is not the eternal Tao.

INT. MEDITATION ROOM - MORNING

NARRATOR
A student approaches the master.

STUDENT
Master, what is the Tao?

MASTER
(calmly)
The Tao that can be spoken is not the true Tao.

STUDENT
But how can I understand something that cannot be described?

MASTER
By not trying to describe it. Experience it instead.

NARRATOR
The student bows and leaves, contemplating the master's words.

FADE OUT.
```

## Produciesta-Specific Tips

### 1. Test with Dry Run

Preview character extraction:

```bash
produciesta /path/to/project --dry-run --autocast --provider apple
```

### 2. Auto-Cast First Time

Let Produciesta extract characters and assign voices:

```bash
produciesta /path/to/project --autocast --provider apple
```

### 3. Validate Fountain Format

Use a Fountain syntax validator before generating:
- [Fountain.io Syntax](https://fountain.io/syntax)
- [Highland 2](https://www.highland2.app/) - Mac app
- [Fade In](https://www.fadeinpro.com/) - Cross-platform

### 4. Character Count

Keep character count manageable:
- Small podcast: 2-4 characters
- Medium podcast: 5-8 characters
- Large podcast: 9+ characters (requires more voice management)

### 5. Narrator as Default

If you have undefined characters, Produciesta can use default voice:

```bash
produciesta /path/to/project \
  --default-voice "apple://com.apple.voice.premium.en-US.Aaron"
```

## Common Mistakes

### ❌ Lowercase Character Names

```fountain
alice
Hello!
```

**Fix**: Use ALL CAPS

```fountain
ALICE
Hello!
```

### ❌ Missing Blank Line

```fountain
ALICE
Hello!
BOB
Hi!
```

**Fix**: Add blank line between characters

```fountain
ALICE
Hello!

BOB
Hi!
```

### ❌ Action Without Narrator

```fountain
Alice walks into the room.

ALICE
Hello!
```

**Fix**: Use narrator for action

```fountain
NARRATOR
Alice walks into the room.

ALICE
Hello!
```

### ❌ Spoken Parentheticals

```fountain
ALICE
(nervously) I don't know what to say.
```

**Fix**: Inline or remove

```fountain
ALICE
I... I don't know what to say.
```

## Resources

### Fountain Tools

- [Highland 2](https://www.highland2.app/) - Mac screenwriting app
- [Fade In](https://www.fadeinpro.com/) - Cross-platform screenwriting
- [Fountain.io](https://fountain.io/) - Official specification
- [VS Code Fountain Extension](https://marketplace.visualstudio.com/items?itemName=piersdeseilligny.betterfountain)

### Learning Resources

- [Fountain Syntax Reference](https://fountain.io/syntax)
- [Fountain for Podcasts Blog](https://blog.fountain.io/)

### Produciesta Resources

- [Produciesta CLI Reference](./produciesta-cli-reference.md)
- [Produciesta README](~/Projects/Produciesta/README.md)

## Quick Reference Card

| Element | Syntax | Example |
|---------|--------|---------|
| Scene Heading | `INT./EXT. LOCATION - TIME` | `INT. CAFE - DAY` |
| Action | Plain text | `Alice enters.` |
| Character | ALL CAPS on own line | `ALICE` |
| Dialogue | Line after character | `Hello!` |
| Parenthetical | `(direction)` | `(whispering)` |
| Transition | ALL CAPS with colon or period | `CUT TO:` |
| Lyrics | `~text~` | `~Happy birthday~` |
| Dual Dialogue | `CHARACTER ^` | `ALICE ^` |
| Centered | `>text<` | `> THE END <` |
| Section | `# text` | `# Act One` |
| Note | `[[text]]` | `[[emphasize]]` |
| Comment | `/* text */` | `/* draft note */` |
| Filter | `{{text}}` | `Hello {{stage note}} world` |
