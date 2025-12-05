Here is the comprehensive, production-ready README.md for OmniScore. This document integrates the language specification, the design philosophy, and the visual rendering standards into a single authoritative source.

🎼 OmniScore

![alt text](https://img.shields.io/badge/spec-v1.0-blueviolet)
![alt text](https://img.shields.io/badge/paradigm-declarative-success)
![alt text](https://img.shields.io/badge/render-SVG-green)
![alt text](https://img.shields.io/badge/license-MIT-blue)

The Universal Text-to-Music Standard.

OmniScore is a declarative language that generates high-fidelity music notation from simple text. It does for music what Markdown does for text and Mermaid does for diagrams. It is designed to be version-controlled, diffable, and embeddable anywhere.

🚀 Quick Start

Input (Code):

code
JavaScript
download
content_copy
expand_less
omniscore
  def pno "Piano" style=standard
  
  measure 1
    pno: c4:4 e4:4 g4:2 |

Output (Visual):

Renders a crisp, vector-based musical staff with a C Major chord.

📐 The Architecture

OmniScore treats music as a coordinate system, not just a set of instructions.

The Canvas (The "Y-Axis"): You define the physics of the staff first (5-line pitch, 6-line tab, or 1-line rhythm).

The Timeline (The "X-Axis"): Time is absolute. Measures are containers that align all tracks vertically.

The Glyph (The Event): Data points placed at (time, vertical_pos).

📘 Language Specification
1. File Structure

An .omni file has three phases: Meta, Definitions, and Flow.

code
JavaScript
download
content_copy
expand_less
omniscore
  %% 1. META: Global song settings
  meta { title: "Opus 1", tempo: 120, time: 4/4 }

  %% 2. DEFINITIONS: Instantiating the instruments
  def vln "Violin" style=standard clef=treble
  def gtr "Guitar" style=tab      tuning=[E2,A2,D3,G3,B3,E4]
  def drm "Drums"  style=grid     map={k:0, s:4, h:8}

  %% 3. FLOW: The chronological sequence
  measure 1
    vln: ...
    gtr: ...
2. Data Primitives

The fundamental unit is the Event: Value:Duration.Modifiers

Duration (Rhythm)

Durations are "sticky"—if omitted, the previous duration persists.

Syntax	Meaning	Logic
:1	Whole	4 beats
:2	Half	2 beats
:4	Quarter	1 beat
:8	Eighth	0.5 beat
:16	Sixteenth	0.25 beat
.	Dotted	+50% length
~	Tie	Merge with next
Input Types (The "What")

The syntax changes based on the style of the instrument defined.

Style	Syntax	Example	Description
Standard	[Note][Acc][Oct]	c#4, db, f	Scientific Pitch. Octave inferred if omitted.
Tablature	[Fret]-[String]	0-6, 12-1	Coordinate system. String 6 is Low E.
Grid	[Key]	k, s, h	Mapped keys defined in map={}.
Chords	[n1 n2 n3]	[c4 e4 g4]	Stacked group. Duration applies to all.
Canvas	draw(shape, args)	draw(line)	Vector drawing for graphic scores.
3. Modifiers (The "How")

Append modifiers using dot notation (.). Chain them as needed.

Dynamics: .p, .mf, .ff, .sfz

Articulation: .stc (staccato), .acc (accent), .ten (tenuto)

Technique: .pizz, .arco, .palm

Guitar: .bu (bend up), .bd (bend down), .vib (vibrato)

Grouping: .slur / .end

🎨 Visual Rendering Standard

OmniScore does not emulate hand-engraving. It uses a "Semantic Vector" aesthetic designed for screen readability and code mapping.

1. The Design System

Flat & Schematic: No faux-ink textures. Pure geometric shapes.

Color Coding:

Ink Black: Notes, Stems, Beams (The Data).

Light Grey: Staff lines, Bar lines (The Grid).

Blue: Meta-data (Dynamics, Expressions).

Purple: Tablature Numbers.

Interactive:

Hover: Hovering a note highlights the corresponding text code.

Click: Clicking a measure focuses the editor.

2. Layout Logic

Fluid Width: Measures wrap automatically based on container width (responsive).

Vertical Alignment: All tracks in a measure block are visually locked to the same X-axis grid.

🏆 The "Rosetta Stone" Example

A single file demonstrating the full capability of the language: Standard Notation, Tablature, Percussion Grids, and Vector Graphics.

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
    %% Standard notation with dynamics and tuplets
    flt: c5:4.mf d5:8 (3:2 e5:8 f5 g5) a5:4.stc |
    
    %% Guitar Tab with specific string selection and strums
    gtr: r:2          [0-6 2-5 2-4]:2.downstr  |
    
    %% Drum Grid using mapped keys
    prc: k:4  h:8 h   s:4          k:8 k       |
    
    %% Graphic notation (Vector drawing)
    cvs: draw(line, y=10..90, style=zigzag)    |

  measure 2 "Polyphony & Bends"
    %% Polyphony: Two voices on one staff
    flt: {
       v1: c6:2.slur      b5:2.end |
       v2: a5:4    g5:4   f5:2     |
    }
    
    %% Guitar Bends
    gtr: 10-2:2.bu(full)  10-2:2.bd(0) |
    
    %% Drum Rolls
    prc: [k h]:4 [k h]:4  [s h]:2.roll |
    
  measure 3 "Aleatoric/Graphic"
    %% Using the canvas for instructions
    flt: draw(box, t=1..4, text="Improvise") |
    gtr: draw(gliss, y=0-6..12-1)            |
🛠 Implementation Guide

For developers building parsers or plugins:

Parsing: Use a PEG (Parsing Expression Grammar) to tokenize the stream. Normalize all inputs (Notes, Tabs, Hits) into a generic Event object: { time, duration, y_coordinate, modifiers }.

Rendering: Map style to renderer type.

style=standard → VexFlow or SVG Note logic.

style=tab → SVG Text on Lines.

style=grid → SVG Shapes on Matrix.

Integration: Look for omniscore code blocks in Markdown and replace them with the rendered <svg> element.

Specified by the Cognitive Architecture Group, 2025.
