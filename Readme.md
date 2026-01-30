OmniScore 🎼
The Code of Harmony: DevOps for the Modern Orchestral Workflow.
Maintainer: The OmniScore Working Group
License: MIT
Version: 1.0.0-beta
The Vision
We have sent rovers to Mars. We have cracked the human genome. And yet, if you walk into any major symphony orchestra or film scoring stage today, you will find people emailing binary files like Symphony_No_5_Final_v2_REALLY_FINAL_PRINT.mus back and forth, praying they don't overwrite each other's work.
We are treating the most complex collaborative art form—the symphony—as if it were a static painting. We are stuck in the "Save As" era.
OmniScore is the shift to Distributed Version Control. It is a Domain Specific Language (DSL) that does for music what Markdown did for writing and what Mermaid did for diagrams. It treats a symphony not as a file, but as a Repository.
Table of Contents
Introduction
Lexical Structure
Document Structure
Instrument Definitions (The Physics)
The Event Engine: Rhythm & Time
The Pitch Engine
Notational Attributes
The Tablature Engine
The Percussion Engine
Advanced Polyphony
Structure & Flow Control
The Lyric Engine
Layout Directives
Playback Control (The Synth Engine)
Macros & Variables
File Organization & The Repository
Advanced Engraving Controls
Ornamentation & Lines
Microtonality
Visual Styling (The Theme Engine)
Advanced MIDI & Automation
Compiler Directives & Debugging
The Standard Library
Error Reference
Implementation Guidelines
Workflow: Git, CI/CD, and Branching
Formal Grammar (EBNF)
Reference Example
1. Introduction
OmniScore is a declarative, domain-specific language (DSL) describing musical logic, notation, and performance data. Unlike XML-based formats which prioritize visual layout coordinates, OmniScore prioritizes musical intent, utilizing an inference engine to calculate layout at render-time.
The Core Analogy:
OmniScore is to music what Mermaid is to charts.
Just as you write text to generate a flowchart without manually dragging boxes, you write OmniScore code to generate a musical score without manually placing notes.
1.1 Design Philosophy
The language adheres to four core principles:
Inference Over Redundancy ("Sticky State"): Attributes (duration, octave, velocity) persist until changed.
Semantic Separation: The definition of an instrument (its physics) is separated from the event data (the notes).
Human Readability: Source code should be intelligible to a musician without rendering software.
The "Open Measure" Principle: Collaboration is additive. If two authors write to the same measure in different files, the compiler merges them into a single time-slice rather than overwriting.
1.2 The Coordinate System
OmniScore maps music onto a logical grid:
X-Axis (Time): Linear absolute time, segmented by Measure blocks.
Y-Axis (Source): Distinct logical threads defined by Staff IDs.
Z-Axis (Polyphony): Vertical layering within a single time/source coordinate (Voices).
1.3 The Compilation Pipeline
A compliant OmniScore compiler must follow these stages:
Lexing/Parsing: Tokenize the text and validate against the grammar.
Context Building: Process meta and def blocks to establish global physics (Time signatures, Instrument capabilities).
Linearization: Iterate through measure blocks.
Resolve "Sticky" attributes.
Calculate absolute tick positions for every event.
Merge Strategy: Combine additive inputs from multiple sources (The Open Measure).
Rendering: Map the linearized data to the target output (SVG, MIDI, MusicXML).
2. Lexical Structure
2.1 Character Set & Encoding
Source files must be encoded in UTF-8.
Case Sensitivity:
Keywords (def, measure, style) are case-insensitive.
Note Names (c4, C4) are case-insensitive.
Identifiers (vln, Gtr1) are case-sensitive.
String Literals ("Violin") are case-sensitive.
2.2 Whitespace & Formatting
Whitespace (Space U+0020, Tab U+0009, Line Feed U+000A) is generally insignificant and serves only as a token separator.
Indentation: Two-space indentation is the recommended convention for readability but is not syntactically significant.
Line Breaks: Valid statements may span multiple lines.
2.3 Comments
Comments are non-executable text segments used for documentation.
Line Comments: Indicated by a double percentage sign %%. All text following %% on the same line is ignored.
%% This is a comment
c4:4 %% Inline comment


2.4 Literals & Data Types


Type
Syntax
Examples
Description
Integer
[0-9]+
1, 120
Used for octaves, BPM, and repetition counts.
Float
[0-9]+\.[0-9]+
1.5
Used for precise duration multipliers.
String
".*"
"Violin I"
UI Labels and Metadata values.
Pitch
`[a-g][#
b
x]*[0-9]`
TabCoord
[0-9]+-[0-9]+
0-6, 12-2
Format: Fret-String.
Boolean
true
false
Logical flags.
Array
[val, val]
[E2, A2]
Ordered lists.
Map
{ key: val }
{ k:0 }
Key-value pairs for configuration.

3. Document Structure
A valid OmniScore file consists of a single root object containing three optional but sequential sections: Meta, Definitions, and Flow.
3.1 The Root Block
The file must begin with the omniscore keyword.
omniscore
  %% 1. Metadata (Global)
  meta { ... }

  %% 2. Definitions (Setup)
  def ...

  %% 3. Flow (Logic)
  measure 1 ...


3.2 Metadata Scope
The meta block defines global properties.
Syntax: meta { key: value, ... }
Standard Keys:
title (String): The work's title.
composer (String): The author.
tempo (Integer): Global beats per minute (BPM). Default 120.
time (String): Initial time signature. Default 4/4.
key (String): Initial key signature (e.g., C, F#m, Bb). Default C.
swing (Integer): Swing percentage (0-100). Default 0.
4. Instrument Definitions (The Physics)
Before any music can be written, the "instruments" must be defined. This tells the parser how to interpret the data stream (e.g., interpreting 0 as a rest, a fret, or a drum hit).
4.1 The Definition Statement
Syntax: def [ID] [Label] [Attributes]
ID: A unique alphanumeric identifier used to reference the staff in the Logic block (e.g., vln).
Label: The display name for the staff (e.g., "Violin I").
4.2 Staff Styles
The style attribute determines the parsing engine for the staff.
4.2.1 Standard Style (style=standard)
The default engine for pitched instruments.
Input: Pitch Literals (c4) or Rests (r).
Clef: treble, bass, alto, tenor.
Transpose: Integer (semitones). E.g., transpose=+2 for Bb Clarinet.
def flt "Flute" style=standard clef=treble
def sax "Alto Sax" style=standard transpose=+9


4.2.2 Tablature Style (style=tab)
The engine for fretted instruments.
Input: Tab Coordinates (fret-string).
Tuning: Array of pitches representing open strings (low to high).
Capo: Integer representing the fret position of a capo.
%% Standard Guitar
def gtr "Guitar" style=tab tuning=[E2, A2, D3, G3, B3, E4]


4.2.3 Grid Style (style=grid)
The engine for unpitched percussion or rhythmic triggers.
Input: Mapped Characters (k, s, h).
Map: A dictionary linking input characters to vertical staff positions.
def kit "Drum Set" style=grid map={
  k: 0,  %% Kick (Bottom line)
  s: 4,  %% Snare (Middle line)
  h: 8,  %% Hi-Hat (Top space)
  c: 10  %% Crash (Above staff)
}


4.3 Grouping & Bracketing
Staves can be visually grouped using the group block.
group "Strings" symbol=bracket {
  def v1 "Violin I" style=standard
  def v2 "Violin II" style=standard
}


5. The Event Engine: Rhythm & Time
The core of OmniScore's efficiency lies in its handling of time. Unlike formats that require explicit start/stop times for every event, OmniScore treats music as a linear stream of durations.
5.1 Duration Syntax
Duration is denoted by a colon followed by a value (:value).
Logic
Syntax
Musical Equivalent
Quarter
:4
♩
Eighth
:8
♪
Sixteenth
:16
♬
Dotted Quarter
:4.
♩.
Whole
:1
𝅝

5.2 Sticky Attributes (Contextual Inference)
To reduce file size, OmniScore employs "Sticky State" logic. If a duration is omitted from an event, the parser infers it from the immediately preceding event in that staff.
Explicit (Verbose): c4:4 d4:4 e4:4 f4:4
Implicit (Optimized): c4:4 d4 e4 f4
5.3 Tuplets
Tuplets divide a duration into equal parts contrary to the prevailing meter.
Syntax: (events):ratio
%% 3 notes in the time of 2 (Triplets)
(c4 d e):3/2


5.4 Rests
Rests use the literal r.
Standard Rest: r:4
Multi-Measure Rest: r:1 * 4 (Rest for 4 whole notes).
6. The Pitch Engine
6.1 Scientific Pitch Notation
Pitch is defined by a Note Name (A-G), an Accidental, and an Octave Number.
Format: [Step][Accidental][Octave]
Examples: C4 (Middle C), F#5, Bb2.
Sticky Octaves:
Like duration, octaves are sticky. If an octave is omitted, the engine assumes the octave of the previous note.
c4 e g becomes c4 e4 g4.
6.2 Accidentals
#: Sharp
b: Flat
x: Double Sharp
bb: Double Flat
n: Natural
6.3 Chords
Polyphony within a single voice (chords) is denoted by square brackets [].
Syntax: [note note note]:duration
[c4 e4 g4]:4


6.4 Ties
Ties connect two notes of the same pitch to extend duration.
Syntax: ~ (tilde) appended to the first note.
c4:4~ c4:8  %% Ties a quarter to an eighth


7. Notational Attributes
Attributes decorate events with dynamics, articulations, and text. They are appended to the event using dot notation.
Syntax: event:duration.modifier.modifier
7.1 Dynamics
pppp to ffff
sfz, fp
Example: c4:4.ff
7.2 Articulations
.stacc (Staccato)
.acc (Accent)
.ten (Tenuto)
.fermata (Pause)
Example: c4:4.stacc.acc
7.3 Text Instructions
Syntax: event."Text"
c4:4."Sim."


8. The Tablature Engine
8.1 Coordinate Syntax
Tablature uses a fret-string coordinate system.
Fret: Integer (0-24).
String: Integer (1 = High E, 6 = Low E on standard guitar).
Example: 0-6 (Open Low E string).
8.2 Guitar Techniques
Bends: .bu(interval) and .bd(interval).
Slides: .sl or .sl(from).
Legato: .h, .p, .t.
Harmonics: .harm, .ph.
12-2:4.bu(full)


8.3 Strums
Chords in tab are stacked in brackets [].
[0-6 2-5 2-4]:4.down
9. The Percussion Engine
9.1 Map-Based Input
Percussion relies on the map defined in the header. Input is limited to mapped keys.
9.2 Percussion Modifiers
.ghost (Parenthesized note)
.flam (Grace note before hit)
.drag (Double grace note)
.roll (Tremolo/Buzz)
k:4 s:8.ghost s:8.acc


10. Advanced Polyphony
OmniScore supports multi-threaded logic within a single staff using Voice Groups.
10.1 Voice Syntax
Voices are enclosed in curly braces {}.
staff_id: {
  v1: events... |
  v2: events... |
}


10.2 Synchronization Rules
Voices within a group must sum to the same total duration. If v1 contains 4 beats, v2 must also contain 4 beats. The compiler throws a VOICE_SYNC error on mismatch.
11. Structure & Flow Control
11.1 Bar Lines & Repeats
|: - Start Repeat
:| - End Repeat
|| - Double Bar
|] - Final Bar Line
measure 1
  vln: c4 d e f :|


11.2 Volta Brackets (Endings)
Syntax: [number. events ... ]
measure 4
  vln: [1. c4 d e f :| ]
  vln: [2. c4 g4 c5 r | ]


12. The Lyric Engine
Lyrics are handled as a parallel data stream.
12.1 Syllable Mapping
The lyric keyword maps syllables to notes 1-to-1.
Space: New word.
Hyphen -: Syllable within word.
Underscore _: Melisma extension.
measure 1
  vox: c4:4 d4 e4 f4 |
  vox.lyric: "Hel- lo world _"


13. Layout Directives
Explicit breaks for engraving control.
meta { break: system }: Force new line.
meta { break: page }: Force new page.
meta { stretch: 1.5 }: Adjust measure width multiplier.
14. Playback Control (The Synth Engine)
14.1 Instrument Patches
Defined in the definition block using patch.
def pno "Piano" style=standard patch="Acoustic Grand Piano"


14.2 Mixer Attributes
vol: 0-127.
pan: -64 (Left) to 63 (Right).
14.3 Tempo Maps
meta { tempo: 140 }
meta { tempo: [100, 140], curve: linear } (Accelerando).
15. Macros & Variables
Text-substitution macros for repetitive riffs.
Define: macro RiffA = { c4:16 d eb f }
Invoke: $RiffA
Transpose: $RiffA+2 (Shift up 2 semitones).
16. File Organization & The Repository
OmniScore treats a musical work as a Repository of code, structured for collaboration. Large works should use the Master Linker pattern.
16.1 The "Repo" Layout
/my-symphony
├── meta/
│   ├── globals.omni       # Tempo maps, key signatures (The "Physics")
│   └── instruments.omni   # Def blocks: range, transposition, midi-channels
├── src/
│   ├── woodwinds/
│   │   ├── flute_1.omni
│   │   └── oboe.omni
│   ├── percussion/
│   │   └── timpani.omni
│   └── strings/
│       └── violin_1.omni
└── master.omni            # The Master Linker / Root Manifest


16.2 The Master Linker
The root file (master.omni) contains no music. It serves as the entry point for the compiler, importing the physics and the logic.
// master.omni
omniscore
import "meta/globals.omni"
import "meta/instruments.omni"

// Link Sections
import "src/woodwinds/flute_1.omni"
import "src/strings/violin_1.omni"


16.3 The "Open Measure" Implementation
Because imports are additive, multiple files can define content for measure 1.
flute_1.omni writes: measure 1 flt: ...
violin_1.omni writes: measure 1 vln: ...
The compiler merges them. No file locking required.
17. Advanced Engraving Controls
Manual Beaming: .bm (begin) and .bme (end).
Stem Direction: .up, .down, .auto.
Grace Notes: :grace duration (e.g., d4:grace).
18. Ornamentation & Lines
Trills: .tr, .mordent.
Glissando: .gliss (straight), .port (curved).
Arpeggiation: .arp, .arp(up).
Ottava: meta { ottava: "8va" }.
19. Microtonality
Quarter Tones: qs (quarter sharp), qf (quarter flat), tqs, tqf.
Cent Deviation: c4+14:4 (14 cents sharp).
20. Visual Styling (The Theme Engine)
Theme: meta { theme: "jazz" } (Handwritten font).
Color: event.color("red") or .red.
Noteheads: .head("x"), .head("diamond").
21. Advanced MIDI & Automation
CC Messages: event.cc(1, 127) (Mod Wheel Max).
Curves: event.cc(11, [0, 100]) (Expression Swell).
Keyswitches: Defined in def block.
22. Compiler Directives & Debugging
Strict Mode: meta { strict: true } (Disables "sticky" across barlines).
Conditional Compilation: if (midi) { ... }.
23. The Standard Library
Includes constants for clef (treble, bass, perc, tab), tuning (guitar_std, drop_d), and map (gm_standard for percussion).
24. Error Reference
E101 (Fatal): Syntax Error.
E201 (Fatal): Definition Missing.
E301 (Error): Voice Sync Mismatch.
E302 (Error): Time Overflow (Too many beats in measure).
25. Implementation Guidelines
Compilers must implement a state machine to track "Sticky Attributes" (Current Duration, Octave). Logic must be resolved in order: Lexical -> Macro -> Def -> Meta -> Linearization -> Validation -> Rendering.
26. Workflow: Git, CI/CD, and Branching
OmniScore enables professional DevOps workflows for orchestras.
26.1 Branching Strategies
main: The "Rehearsal Ready" state. Always printable.
feature/movement-2: Composer drafts a new movement.
fix/horn-range: Copyist fixes a specific issue in isolation.
26.2 Conflict Resolution
Because OmniScore is text, merge conflicts are readable.
<<<<<<< HEAD
vln: c4:4 e4 g4  // Branch A: Simple triad
=======
vln: c4:8 d e f g a b c // Branch B: Fast run
>>>>>>> feature/fast-run


26.3 CI/CD for Music
A "Build Server" can run automated checks on every push:
Validation: Check for E301 (Rhythm errors).
Range Check: Ensure no notes exceed instrument capabilities.
Artifact Generation: Auto-build PDFs and MIDI for Conductor, Parts, and Audio.
27. Formal Grammar (EBNF)
Program         ::= 'omniscore' MetaBlock? DefBlock+ MeasureBlock+
MetaBlock       ::= 'meta' '{' KeyValuePair (',' KeyValuePair)* '}'
DefBlock        ::= 'def' Identifier StringLiteral Attribute*
MeasureBlock    ::= 'measure' MeasureRange MetaBlock? StaffLogic*
StaffLogic      ::= Identifier ':' (Event | BarLine | VoiceGroup)+
VoiceGroup      ::= '{' (Identifier ':' Event+)+ '}'
Event           ::= (Note | Chord | Rest) Duration? Modifier*
Note            ::= PitchLiteral | TabCoord | PercussionKey
Chord           ::= '[' Note+ ']'
Duration        ::= ':' Value Dot*
Modifier        ::= '.' Identifier ('(' Args ')')?


28. Reference Example
The "Kitchen Sink" suite demonstrating multiple engines in one file.
omniscore
  meta { title: "OmniScore Reference Suite", tempo: 130, theme: "jazz" }

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
    %% SAX: Polyphonic split
    sax: {
      v1: $LickA c5:2.fermata |
      v2: g4:1.fermata        |
    }
    
    %% GUITAR: Pitch bend
    gtr: 12-2:2.bu(full) 12-2.bd(0) |
    
    %% DRUMS: Fill
    drm: s:16 s s s t1 t1 t2 t2 c:1 |


