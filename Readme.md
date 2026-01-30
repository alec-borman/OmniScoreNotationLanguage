# **OmniScore: The Universal Music Language**

**Maintainer:** The OmniScore Working Group  
**License:** MIT  
**Current Version:** 1.0.0 (Draft)

> **OmniScore is to music what Mermaid is to charts.**  
> It moves music composition from the "Save As" era to the Modern DevOps era, treating music as structured, version-controllable code.

---

## **Table of Contents**

1.  [Introduction & Philosophy](#1-introduction--philosophy)
2.  [Lexical Structure](#2-lexical-structure)
3.  [Document Structure](#3-document-structure)
4.  [Instrument Definitions (The Physics)](#4-instrument-definitions-the-physics)
5.  [The Event Engine: Rhythm & Time](#5-the-event-engine-rhythm--time)
6.  [The Pitch Engine](#6-the-pitch-engine)
7.  [Notational Attributes](#7-notational-attributes)
8.  [The Tablature Engine](#8-the-tablature-engine)
9.  [The Percussion Engine](#9-the-percussion-engine)
10. [Advanced Polyphony](#10-advanced-polyphony)
11. [Structure & Flow Control](#11-structure--flow-control)
12. [The Lyric Engine](#12-the-lyric-engine)
13. [Layout Directives](#13-layout-directives)
14. [Playback Control (The Synth Engine)](#14-playback-control-the-synth-engine)
15. [Macros & Variables](#15-macros--variables)
16. [The Repo Layout (File Organization)](#16-the-repo-layout-file-organization)
17. [Collaborative Workflow (Branching)](#17-collaborative-workflow-branching)
18. [Advanced Engraving Controls](#18-advanced-engraving-controls)
19. [Ornamentation & Lines](#19-ornamentation--lines)
20. [Microtonality](#20-microtonality)
21. [Visual Styling (The Theme Engine)](#21-visual-styling-the-theme-engine)
22. [Advanced MIDI & Automation](#22-advanced-midi--automation)
23. [Compiler Directives & Debugging](#23-compiler-directives--debugging)
24. [The Standard Library](#24-the-standard-library)
25. [Error Reference](#25-error-reference)
26. [Implementation Guidelines](#26-implementation-guidelines)
27. [Interoperability & Build Targets](#27-interoperability--build-targets)
28. [Formal Grammar (EBNF)](#28-formal-grammar-ebnf)
29. [Reference Example](#29-reference-example)

---

## **1. Introduction & Philosophy**

OmniScore is a declarative, domain-specific language (DSL) describing musical logic, notation, and performance data. Unlike XML-based formats (MusicXML) or binary blobs (Sibelius/Finale) which prioritize visual layout coordinates, OmniScore prioritizes **musical intent**.

### **1.1 Why OmniScore?**

*   **Human Readable:** Read and write scores in a text editor. No GUI required.
*   **Git-Native:** Solves the "versioning nightmare" of binary files. Handle merge conflicts with standard text-based tools.
*   **Inference Over Redundancy:** Attributes (duration, octave, velocity) persist until changed. This is known as "Sticky State" logic.
*   **Semantic Separation:** The definition of an instrument (its physics) is separated from the event data (the notes).

### **1.2 The Coordinate System**

OmniScore maps music onto a logical grid:
*   **X-Axis (Time):** Linear absolute time, segmented by Measure blocks.
*   **Y-Axis (Source):** Distinct logical threads defined by Staff IDs.
*   **Z-Axis (Polyphony):** Vertical layering within a single time/source coordinate (Voices).

### **1.3 The Compilation Pipeline**

The `omnic` compiler follows these stages:
1.  **Context Building:** Process global physics (Time signatures, Instrument capabilities).
2.  **Linearization:** Resolve "Sticky" attributes and calculate absolute tick positions.
3.  **Rendering:** Map data to target views (Conductor Score PDF, Individual Part PDF, MIDI, MusicXML).

---

## **2. Lexical Structure**

### **2.1 Character Set & Encoding**
*   Source files must be encoded in **UTF-8**.
*   **Case Sensitivity:** Keywords (`def`) and Note Names (`c4`) are case-insensitive. Identifiers (`vln`) and Strings (`"Violin"`) are case-sensitive.

### **2.2 Comments**
*   **Line Comments:** `%%` ignores text until end of line.

```omniscore
c4:4 %% This is a comment
```

### **2.3 Literals & Data Types**

| Type | Syntax | Examples | Description |
| :--- | :--- | :--- | :--- |
| **Integer** | `[0-9]+` | `1`, `120` | Octaves, BPM. |
| **Float** | `[0-9]+\.[0-9]+` | `1.5` | Precise durations. |
| **String** | `".*"` | `"Violin I"` | UI Labels. |
| **Pitch** | `[a-g][#|b|x]*[0-9]` | `c4`, `f#5` | Scientific Pitch. |
| **TabCoord** | `[0-9]+-[0-9]+` | `0-6`, `12-2` | Fret-String. |

---

## **3. Document Structure**

A valid OmniScore file consists of a root object containing Meta, Definitions, and Flow.

```omniscore
omniscore
  %% 1. Metadata (Global)
  meta { title: "Symphony No. 1", tempo: 120 }

  %% 2. Definitions (The Physics)
  def vln "Violin" style=standard

  %% 3. Flow (The Logic)
  measure 1
    vln: c4:4 e g c5
```

---

## **4. Instrument Definitions (The Physics)**

Definitions tell the parser how to interpret the data stream (e.g., interpreting `0` as a rest, a fret, or a drum hit).

### **4.1 The Definition Statement**
*   **Syntax:** `def [ID] [Label] [Attributes]`

### **4.2 Staff Styles**

#### **4.2.1 Standard Style (`style=standard`)**
Default for pitched instruments.
```omniscore
def flt "Flute" style=standard clef=treble
def sax "Alto Sax" style=standard transpose=+9
```

#### **4.2.2 Tablature Style (`style=tab`)**
Engine for fretted instruments. Requires a `tuning` array.
```omniscore
def gtr "Guitar" style=tab tuning=[E2, A2, D3, G3, B3, E4]
```

#### **4.2.3 Grid Style (`style=grid`)**
Engine for percussion. Requires a mapping object.
```omniscore
def kit "Drum Set" style=grid map={ k:0, s:4, h:8 }
```

---

## **5. The Event Engine: Rhythm & Time**

OmniScore treats music as a linear stream of durations.

### **5.1 Sticky Attributes**
If a duration is omitted, the parser infers it from the previous event.

```omniscore
%% Explicit: c4:4 d4:4 e4:4
%% Implicit: c4:4 d4 e4
```

### **5.2 Duration Syntax**
*   Quarter: `:4`
*   Eighth: `:8`
*   Dotted: `:4.`
*   Whole: `:1`

### **5.3 Tuplets**
Syntax: `(events):ratio`.
```omniscore
(c4 d e):3/2  %% Triplet (3 in space of 2)
```

---

## **6. The Pitch Engine**

### **6.1 Scientific Pitch Notation**
Pitch is defined by Step (A-G), Accidental, and Octave.
*   **Sticky Octaves:** The engine strictly uses the last declared integer.
*   **Example:** `c4 e g` becomes `c4 e4 g4`.

### **6.2 Chords**
Polyphony within a single voice is denoted by square brackets `[]`.
```omniscore
[c4 e4 g4]:4
```

### **6.3 Ties**
Syntax: `~` appended to the note.
```omniscore
c4:4~ c4:8
```

---

## **7. Notational Attributes**

Attributes are appended using dot notation.

*   **Dynamics:** `.pp`, `.ff`, `.sfz`
*   **Articulations:** `.stacc`, `.acc`, `.ten`, `.fermata`
*   **Text:** `event."String"`

```omniscore
c4:4.stacc.ff."Sim."
```

---

## **8. The Tablature Engine**

### **8.1 Coordinate Syntax**
Format: `Fret-String`.
*   `0-6`: Open Low E.
*   `12-2`: 12th fret, B string.

### **8.2 Techniques**
*   **Bends:** `.bu(full)`, `.bd`
*   **Slides:** `.sl`
*   **Legato:** `.h` (Hammer), `.p` (Pull)

```omniscore
12-2:4.bu(full) 12-2.bd(0).p
```

---

## **9. The Percussion Engine**

Input is limited to keys defined in the instrument `map`.

*   **Modifiers:** `.ghost`, `.flam`, `.roll`

```omniscore
k:4 s:8.ghost s:8.acc
```

---

## **10. Advanced Polyphony**

### **10.1 Voice Groups**
Split a staff into multiple logical threads using `{}`.

```omniscore
piano: {
  v1: c5:4 d5 e5 f5 |
  v2: c4:1          |
}
```

**Constraint:** All voices in a group must sum to the exact same duration.

---

## **11. Structure & Flow Control**

### **11.1 Bar Lines**
*   `|` Measure end
*   `|:` Start Repeat
*   `:|` End Repeat
*   `|]` Final Bar

### **11.2 Voltas (Endings)**
Syntax: `[1. events...]`.

```omniscore
measure 4
  vln: [1. c4 d e f :| ]
measure 5
  vln: [2. c4 g4 c5 r | ]
```

---

## **12. The Lyric Engine**

Lyrics are a parallel stream mapped to a staff. Syllables map 1-to-1 with notes.

```omniscore
vox: c4:4 d4 e4
vox.lyric: "Hel- lo world"
```

---

## **13. Layout Directives**

*   `meta { break: system }`: Force new line.
*   `meta { stretch: 1.5 }`: Widen measure spacing.

---

## **14. Playback Control (The Synth Engine)**

### **14.1 Mixer**
*   `vol`: 0-127
*   `pan`: -64 (Left) to 63 (Right)

```omniscore
meta { vln.vol: 80, vln.pan: -64 }
```

### **14.2 Tempo Maps**
`meta { tempo: [100, 140], curve: linear }`

---

## **15. Macros & Variables**

Macros reduce redundancy for repetitive riffs.

```omniscore
macro RiffA = { c4:16 d eb f }
measure 1
  gtr: $RiffA $RiffA+2 | %% +2 Transposes the macro
```

---

## **16. The Repo Layout (File Organization)**

For professional ensembles, OmniScore mandates a directory structure known as the **Additive Compilation Model**. This turns a musical work into a distributed repository.

### **16.1 The "Open Measure" Principle**
In standard programming, redefining a function throws an error. In OmniScore, collaboration is **additive**. If `violin.omni` defines Measure 1 and `cello.omni` also defines Measure 1, the compiler merges them into a single time-slice at build time.

### **16.2 Directory Structure**

```text
/Project_Root
  ├── omni.config              # Compiler settings (page size, fonts)
  ├── master.omni              # The "Linker" (Single Source of Truth)
  ├── /build                   # Generated artifacts (PDF, MIDI, WAV)
  └── /src
      ├── /meta
      │   ├── globals.omni     # Tempo maps, Time Sigs, Rehearsal Marks
      │   └── defs.omni        # Instrument Definitions (The Physics)
      └── /sections            # Modular musical content
          ├── /ww              # Woodwinds (flute.omni, oboe.omni)
          ├── /br              # Brass
          ├── /perc            # Percussion
          └── /str             # Strings
```

### **16.3 The Master File**
The `master.omni` file simply imports the necessary components.

```omniscore
omniscore
  import "src/meta/defs.omni"
  import "src/meta/globals.omni"
  import "src/sections/str/violin1.omni"
  import "src/sections/str/cello.omni"
```

---

## **17. Collaborative Workflow (Branching)**

OmniScore explicitly recommends adopting software development branching strategies for composition.

### **17.1 Branching Strategy**
*   `main`: The "Rehearsal Ready" score. Always compile-able.
*   `feature/movement-2`: Composer drafts a new section.
*   `fix/measure-42-range`: A copyist fixes a specific range issue for the Horns.

### **17.2 Conflict Resolution**
When two composers edit the same line, you get a readable Git Merge Conflict rather than a corrupted binary file.

```omniscore
<<<<<<< HEAD
vln: c4:4 e4 g4
=======
vln: c4:8 d e f g a b c
>>>>>>> feature/fast-run
```
**Resolution:** Delete the markers and the unwanted logic. Commit the result.

---

## **18. Advanced Engraving Controls**

*   **Manual Beaming:** `.bm` (Start), `.bme` (End).
*   **Stem Direction:** `.up`, `.down`.
*   **Grace Notes:** `note:grace`.

---

## **19. Ornamentation & Lines**

*   **Ornaments:** `.tr`, `.turn`, `.mordent`.
*   **Lines:** `.gliss` (straight), `.port` (curved).
*   **Arpeggios:** `.arp`, `.arp(up)`.
*   **Ottava:** `meta { ottava: "8va" }`.

---

## **20. Microtonality**

*   **Quarter Tones:** `qs` (quarter sharp), `qf` (quarter flat).
*   **Cents:** `c4+14` (C4 tuned 14 cents sharp).

---

## **21. Visual Styling (The Theme Engine)**

The visual layer is controlled via metadata.

*   `theme: "standard"` (Bravura font, classical).
*   `theme: "jazz"` (Petaluma font, handwritten).
*   `theme: "educational"` (Color-coded notes).

```omniscore
c4:4.color("red").head("x")
```

---

## **22. Advanced MIDI & Automation**

*   **CC Messages:** `event.cc(1, 127)` (Mod wheel max).
*   **Automation Curves:** `event.cc(11, [0, 100])` (Expression swell).
*   **Keyswitches:** Defined in instrument `def`.

---

## **23. Compiler Directives & Debugging**

*   **Strict Mode:** `meta { strict: true }` forces explicit attribute declarations.
*   **Conditional Compilation:**
    ```omniscore
    if (midi) { keys: c2:1 }       %% Audio only
    if (score) { text: "Ad lib" }  %% Visual only
    ```

---

## **24. The Standard Library**

*   **Clefs:** `treble`, `bass`, `alto`, `tenor`, `perc`, `tab`.
*   **Tunings:** `guitar_std`, `guitar_drop_d`, `bass_std`.
*   **Maps:** `gm_standard` (General MIDI percussion).

---

## **25. Error Reference**

*   **E101 SYNTAX_ERR:** Malformed token.
*   **E201 DEF_MISSING:** Undefined staff ID.
*   **E301 VOICE_SYNC:** Voice group duration mismatch.
*   **E302 TIME_OVERFLOW:** Measures contain too many beats.

---

## **26. Implementation Guidelines**

Parsers must maintain a state machine tracking "Sticky Attributes" (Last Duration, Last Octave). The resolution order is:
1.  **Lexing**
2.  **Macro Expansion**
3.  **Definition Registry**
4.  **Meta Processing**
5.  **Linearization (Sticky Resolution)**
6.  **Rendering**

---

## **27. Interoperability & Build Targets**

OmniScore uses View Definitions to generate specific assets for specific stakeholders via the CLI.

### **27.1 Build Commands (CI/CD)**

```bash
# Generate the full conductor score
omnic -i master.omni --view=conductor

# Generate a Pro-Tools ready MIDI map
omnic -i master.omni --target=midi

# Generate only the percussion parts
omnic -i master.omni --view=percussion_section
```

### **27.2 Export Formats**
*   **MusicXML:** `def` -> Part, `measure` -> Measure.
*   **MIDI:** `def` -> Track. Articulations (.stacc) affect duration.

---

## **28. Formal Grammar (EBNF)**

```ebnf
Program         ::= 'omniscore' MetaBlock? DefBlock+ MeasureBlock+
MeasureBlock    ::= 'measure' MeasureRange MetaBlock? StaffLogic*
StaffLogic      ::= Identifier ':' (Event | BarLine | VoiceGroup)+
Event           ::= (Note | Chord | Rest) Duration? Modifier*
Note            ::= PitchLiteral | TabCoord | PercussionKey
```

---

## **29. Reference Example**

A "Kitchen Sink" example demonstrating the integration of Standard, Tab, and Percussion engines.

```omniscore
omniscore
  meta { title: "OmniScore Reference", tempo: 130, style: "Jazz" }

  %% 1. DEFINITIONS
  group "Rhythm Section" symbol=bracket {
    def sax "Tenor Sax" style=standard clef=treble transpose=-14
    def gtr "Guitar"    style=tab       tuning=guitar_std
    def drm "Drum Kit"  style=grid      map=gm_standard
  }

  %% 2. MACROS
  macro LickA = { c5:16 d eb f g f eb d }

  %% 3. LOGIC
  measure 1
    meta { time: 4/4 }
    
    %% SAX: Sticky duration logic + Articulation
    sax: c4:4.accent e g c5.stacc |

    %% GUITAR: Tablature + Strumming
    gtr: [0-6 2-5 2-4]:4.down [0-6 2-5 2-4].up r:2 |

    %% DRUMS: Complex syncopation
    drm: k:8. s:16 k:8 s k s k s:4.roll |

  measure 2
    %% SAX: Polyphonic split (Harmonizing itself)
    sax: {
      v1: $LickA c5:2.fermata |
      v2: g4:1.fermata        |
    }
    
    %% GUITAR: Pitch bend technique
    gtr: 12-2:2.bu(full) 12-2.bd(0) |
```
