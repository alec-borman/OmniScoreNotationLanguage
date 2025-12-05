Here is the complete, high-density specification for OmniScore. It functions as both a language definition and a user manual.

OMNISCORE SPECIFICATION v1.0
1. FILE ANATOMY

An OmniScore file consists of a Header (metadata), Definitions (instruments/staves), and Flow (the timeline).

code
JavaScript
download
content_copy
expand_less
omniscore
  %% HEADER
  meta { title: "Opus 1", tempo: 120, time: 4/4 }

  %% DEFINITIONS
  def vln "Violin" style=standard clef=treble
  def gtr "Guitar" style=tab strings=6 tuning=[E2,A2,D3,G3,B3,E4]
  def drm "Drums"  style=grid map={k:0, s:4, h:8} %% Custom vertical mapping

  %% FLOW
  measure 1
    vln: c4:4   e4:4   g4:2   |          %% Track: Data
    gtr: 0-6:4  2-5:4  3-5:2  |          %% Fret-String:Duration
    drm: k:4    h:4    s:4    |          %% Key:Duration
2. DATA PRIMITIVES

The fundamental unit is the Event: Value:Duration.Modifiers

A. Duration & Rhythm

Based on division of a whole note.
| Syntax | Meaning | Example |
| :--- | :--- | :--- |
| :1 | Whole | c4:1 |
| :2 | Half | c4:2 |
| :4 | Quarter | c4:4 |
| :8 | Eighth | c4:8 |
| :16 | Sixteenth | c4:16 |
| . | Dotted | c4:4. (Dotted quarter) |
| ~ | Tie | c4:4~c4:8 |
| r | Rest | r:4 |

Optimization: Duration is sticky. c4:4 d e f means all are quarter notes.

B. Input Values (The "What")

The syntax changes based on the style of the instrument defined.

Style	Syntax	Logic	Example
Standard	[Note][Acc][Oct]	Scientific Pitch	c#4, db5, f (infer octave)
Tablature	[Fret]-[String]	Coordinate	0-6 (Open E), 12-1 (High E)
Grid/Perc	[Key]	Mapped Keys	k (Kick), s (Snare)
Chords	[n1 n2 n3]	Stacked Group	[c4 e4 g4]:2
Graphic	draw(shape, args)	Canvas Draw	draw(line, y=50..100)
3. MODIFIERS (THE "HOW")

Append modifiers using dot notation (.). Chain them as needed.

Category	Syntax	Description
Dynamics	.p, .mf, .ff	Standard dynamic markings
Articulation	.stc, .acc, .ten	Staccato, Accent, Tenuto
Ornament	.tr, .turn, .fer	Trill, Turn, Fermata
Technique	.pizz, .arco, .palm	Instrument specific text
Guitar	.bu, .bd, .vib	Bend Up, Bend Down, Vibrato
Grouping	.slur, .end	Start/End phrasing slur

Example: c4:4.stc.ff (Quarter note C, staccato, fortissimo)

4. ADVANCED STRUCTURES
Polyphony (Voices)

Split a single staff into multiple independent voices using { }.

code
JavaScript
download
content_copy
expand_less
pno: {
  v1: c5:4 d5 e5 c5 |  %% Stems Up
  v2: c4:2   g4:2   |  %% Stems Down
}
Tuplets

Override binary rhythm with (ratio: code).

code
JavaScript
download
content_copy
expand_less
vln: (3:2 c8 d8 e8)   %% 3 notes in the time of 2 (Triplet)
Lyrics & Annotations

Text tracks sync to the beat structure of the target (link=id).

code
JavaScript
download
content_copy
expand_less
def vox "Vocals" style=standard
def lyr "Lyrics" style=text link=vox

measure 1
  vox: c4   d4   e4   c4 |
  lyr: "Fra" "re" "Jac" "ques" |
5. THE REFERENCE SCORE

A single code block demonstrating every feature of the language.

code
JavaScript
download
content_copy
expand_less
omniscore
  %% 1. SETUP
  meta { title: "The Rosetta Test", time: 4/4, tempo: 110 }
  
  def flt "Flute"     style=standard clef=treble
  def gtr "Guitar"    style=tab strings=6
  def prc "Percussion" style=grid map={ k:0, s:2, h:4 }
  def cvs "Effects"   style=canvas range=0..100 height=30px

  %% 2. MUSIC
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
