![Version](https://img.shields.io/badge/spec-v1.0-blueviolet) ![Type](https://img.shields.io/badge/paradigm-declarative-success) ![License](https://img.shields.io/badge/license-MIT-blue)

**The Universal Music Notation Standard.**  
OmniScore allows you to write complex musical structures—from orchestral scores to guitar tabs and drum grids—using a unified, declarative text syntax. It is designed to be embedded in Markdown, diffed in Git, and rendered anywhere.

---

## ⚡ Quick Start

```javascript
omniscore
  def pno "Piano" style=standard
  
  measure 1
    pno: c4:4 e4:4 g4:2 |
📘 Language Specification
1. File Anatomy

An .omni file is processed in three phases: Meta, Definitions, and Flow.

code
JavaScript
download
content_copy
expand_less
omniscore
  %% 1. META: Global settings
  meta { title: "Opus 1", tempo: 120, time: 4/4 }

  %% 2. DEFINITIONS: The instruments (The "Y-Axis")
  def vln "Violin" style=standard clef=treble
  def gtr "Guitar" style=tab      tuning=[E2,A2,D3,G3,B3,E4]
  def drm "Drums"  style=grid     map={k:0, s:4, h:8}

  %% 3. FLOW: The Timeline (The "X-Axis")
  measure 1
    vln: c4:4   e4:4   g4:2   |  %% Standard Notation
    gtr: 0-6:4  2-5:4  3-5:2  |  %% Tablature
    drm: k:4    h:4    s:2    |  %% Grid Map
2. Data Primitives

The fundamental unit is the Event: Value:Duration.Modifiers

Duration (Rhythm)

Durations are sticky; if omitted, the previous duration persists.

Syntax	Meaning	Example
:1	Whole	c4:1
:2	Half	c4:2
:4	Quarter	c4:4
:8	Eighth	c4:8
:16	Sixteenth	c4:16
.	Dotted	c4:4.
r	Rest	r:4
Input Values (The "What")

Input syntax adapts to the instrument definition.

Style	Syntax	Logic	Example
Standard	[Note][Acc][Oct]	Scientific Pitch	c#4, db, f (infer octave)
Tablature	[Fret]-[String]	Coordinate	0-6 (Open E), 12-1 (High E)
Grid	[Key]	Mapped Keys	k (Kick), s (Snare)
Chords	[n1 n2 n3]	Stacked Group	[c4 e4 g4]:2
Canvas	draw(shape, args)	Vector Draw	draw(line, y=10..90)
3. Modifiers (The "How")

Append modifiers using dot notation (.). Chain them as needed.

Category	Syntax	Description
Dynamics	.p, .mf, .ff	Standard dynamic markings
Articulation	.stc, .acc, .ten	Staccato, Accent, Tenuto
Technique	.pizz, .arco, .palm	Instrument specific text
Guitar	.bu, .bd, .vib	Bend Up, Bend Down, Vibrato
Grouping	.slur, .end	Start/End phrasing slur
🧠 Advanced Structures
Polyphony

Split a single staff into voices using { }.

code
JavaScript
download
content_copy
expand_less
pno: {
  v1: c5:4 d5 e5 c5 |  %% Voice 1 (Stems Up)
  v2: c4:1          |  %% Voice 2 (Stems Down)
}
Tuplets

Override binary rhythm with (ratio: events).

code
JavaScript
download
content_copy
expand_less
vln: (3:2 c8 d8 e8)   %% Triplet (3 notes in time of 2)
Lyrics & Sync

Text tracks sync to the rhythmic structure of a parent track (link=id).

code
JavaScript
download
content_copy
expand_less
def vox "Voice" style=standard
def lyr "Text"  style=text link=vox

measure 1
  vox: c4    d4   e4    c4 |
  lyr: "Bro" "ther" "John" "_" |
🏆 The Rosetta Stone Example

A single block demonstrating total language capability.

code
JavaScript
download
content_copy
expand_less
omniscore
  meta { title: "The Rosetta Test", time: 4/4, tempo: 110 }
  
  %% DEFINITIONS
  def flt "Flute"      style=standard clef=treble
  def gtr "Guitar"     style=tab      strings=6
  def prc "Percussion" style=grid     map={ k:0, s:2, h:4 }
  def cvs "Effects"    style=canvas   range=0..100 height=30px

  %% THE MUSIC
  measure 1 "Exposition"
    flt: c5:4.mf d5:8 (3:2 e5:8 f5 g5) a5:4.stc |
    gtr: r:2          [0-6 2-5 2-4]:2.downstr  |
    prc: k:4  h:8 h   s:4          k:8 k       |
    cvs: draw(line, y=10..90, style=zigzag)    |

  measure 2 "Polyphony & Bends"
    flt: {
       v1: c6:2.slur      b5:2.end |
       v2: a5:4    g5:4   f5:2     |
    }
    gtr: 10-2:2.bu(full)  10-2:2.bd(0) |
    prc: [k h]:4 [k h]:4  [s h]:2.roll |
    
  measure 3 "Aleatoric/Graphic"
    flt: draw(box, t=1..4, text="Improvise") |
    gtr: draw(gliss, y=0-6..12-1)            |
code
Code
download
content_copy
expand_less
