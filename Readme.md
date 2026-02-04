OmniScore Reference Compiler (omnic)

OmniScore is a declarative, domain-specific language (DSL) for music notation. Unlike traditional formats that focus on visual coordinates (like where a note sits on a page), OmniScore focuses on musical intent. It uses a deterministic inference engine to calculate timing, octaves, and layout at render-time.

This repository contains omnic, the reference compiler for OmniScore v2.0.

✨ Key Features

Sticky State Inference: Stop repeating yourself. Durations and octaves persist until you change them.

Physics-Based Definitions: Define your instruments (physics) separately from your notes (logic).

Rational Time Engine: Built-in support for complex tuplets and perfect rhythmic alignment using fraction-based math (no floating-point rounding errors).

Multi-Phase Pipeline:

Lexing: High-speed tokenization via Logos.

Parsing: Recursive-descent AST generation via Chumsky.

Linearization: Resolution of the "Sticky State" into a flat timeline of events.

🚀 Getting Started

Prerequisites

Rust (1.70+)

Cargo (included with Rust)

Installation

Clone the repository and build the release binary:

git clone [https://github.com/alec-borman/OmniScoreNotationLanguage.git](https://github.com/alec-borman/OmniScoreNotationLanguage.git)
cd OmniScoreNotationLanguage
cargo build --release


The executable will be located at ./target/release/omnic.exe.

🛠 Usage

To compile an OmniScore file and view the inferred timeline:

./omnic --input your_score.omni


Example Input (test.omni)

omniscore {
    meta { title: "Simple Scale", tempo: 120 }
    
    def vln "Violin" style=standard
    
    measure 1 { 
        vln: c4:4 d e f | 
    }
}


📖 Specification

The full language definition, including grammar and musical logic rules, can be found in omniscore-specification.md.

🗺 Roadmap

[x] Phase 1: Lexical Analysis

[x] Phase 2: AST Parsing

[x] Phase 3: Time Inference Engine

[ ] Phase 4: MIDI Backend Export

[ ] Phase 5: SVG/PDF Engraving Engine

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

Created by alec-borman
