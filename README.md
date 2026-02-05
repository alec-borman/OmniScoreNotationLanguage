# Tenuto Reference Compiler (`tenutoc`) v2.0

**The Declarative, Physics-Based Domain Specific Language for Musical Intent**

[![Release](https://img.shields.io/badge/release-v2.0.0-green)](https://github.com/alec-borman/TenutoNotationLanguage/releases)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

**Tenuto** is a high-performance domain-specific language (DSL) designed to bridge the "Semantic Gap" between visual engraving formats (like MusicXML) and mechanical performance protocols (like MIDI).

While traditional formats force a binary choice between layout coordinates and event lists, Tenuto treats musical composition as a **declarative programming task**. It employs a rigid ontological separation between **Instrument Physics** (what an instrument *can* do) and **Musical Logic** (what the instrument *must* do), compiled via a **Rational Temporal Engine** that eliminates floating-point drift.

`tenutoc` is the official reference compiler, written in **Rust**, offering millisecond compilation times and zero-loss MIDI export.

---

## 🚀 The v2.0 Milestone (Feature Complete)

As of **v2.0**, the core "Physics-Based" pipeline is fully operational. The compiler successfully transforms declarative source text into performance-ready MIDI data through three completed phases:

1.  **Phase I (Frontend):** High-speed lexical analysis and parsing using **Logos** and **Chumsky**.
2.  **Phase II (Inference Engine):** A context-aware linearizer that resolves "Sticky State," creates absolute timelines, and manages polyphonic voice synchronization.
3.  **Phase III (Backend):** Native **MIDI Export** via the `midly` crate, supporting 1920 PPQ resolution for complex tuplets.

---

## 🧠 Core Philosophy & Architecture

Tenuto v2.0 challenges the status quo of digital music representation through three architectural pillars:

### 1. Contextual Persistence ("Sticky State")
Musical notation is inherently stateful. Unlike **MusicXML**, which suffers from a "verbosity crisis" by requiring explicit definitions for every note (pitch, octave, duration), Tenuto utilizes a state machine where attributes persist until changed.
*   **The Result:** A drastic reduction in token count and higher human readability.
*   *Example:* `c4:4 d e f` implies that D, E, and F are also quarter notes in octave 4.

### 2. Rational Temporal Arithmetic (The "Exactness Hypothesis")
Standard DAWs (Ableton, Logic) often rely on floating-point math or low-resolution ticks (960 PPQ), leading to "quantization drift" and "jitter" in complex polyrhythms over time.
*   **The Solution:** Tenuto stores time as exact fractions ($\mathbb{Q}$), ensuring that nested tuplets (e.g., $1/3$ inside $1/5$) remain mathematically perfect regardless of the score's duration. This aligns with the precision required for **MIDI 2.0** Jitter Reduction.

### 3. Separation of Physics and Logic
Unlike **Csound** or **LilyPond**, where physical constraints (frequency ranges, transposition) are often hard-coded into the musical score, Tenuto separates them.
*   **Physics:** Defined in `def` blocks (Tuning, Range, Patch).
*   **Logic:** Defined in `measure` blocks (Notes, Rhythms).
*   *Benefit:* A violin melody can be reassigned to a cello, and the compiler automatically handles the transposition and range validation.

---

## 📦 Installation

**Pre-compiled Binaries:**
Download the latest release for Windows, macOS, or Linux from the [Releases Page](https://github.com/alec-borman/TenutoNotationLanguage/releases).

**Build from Source (Rust):**
```bash
git clone https://github.com/alec-borman/TenutoNotationLanguage.git
cd TenutoNotationLanguage
cargo build --release
```
*Note: Tenuto outperforms Python-based toolkits (like music21) by orders of magnitude in execution time and memory safety due to its Rust architecture.*

---

## ⚡ Quick Start

### 1. Create a Source File (`composition.ten`)
```rust
tenuto {
    // 1. Meta Configuration
    meta { 
        title: "Phase III Test", 
        tempo: 120 
    }

    // 2. Instrument Definition (Physics)
    def vln "Violin I" patch="Violin"

    // 3. Musical Logic (Sticky State & Tuplets)
    measure 1 {
        // Sticky: Octave 4, Quarter notes inferred after C4
        vln: c4:4 d e f | 
    }
    
    measure 2 {
        // Complex Tuplet: 3 notes in the time of 2
        vln: (g:8 a b):3/2 c5:2 |
    }
}
```

### 2. Compile to MIDI
```bash
./tenutoc --input composition.ten --output composition.mid
```

### 3. Output
The compiler creates a Standard MIDI File (SMF) with:
*   **Track 1:** Conductor Track (Tempo/Time Signature Map).
*   **Track 2:** "Violin I" (Program Change 40, Note On/Off events at 1920 PPQ resolution).

---

## 🗺️ Development Roadmap

Tenuto is strictly adhering to a phased rollout. We have achieved **Tier 3 (Reference)** capability for audio generation.

| Phase | Component | Status | Description |
| :--- | :--- | :--- | :--- |
| **I** | **Lexer & Parser** | ✅ **Complete** | Logos/Chumsky implementation. Handles nested blocks and complex literals. |
| **II** | **Inference Engine** | ✅ **Complete** | Rational arithmetic, voice leading, and sticky state resolution. |
| **III** | **MIDI Export** | ✅ **Complete** | `midly` integration. High-precision SMF generation. |
| **IV** | MusicXML Export | ⏳ Planned v2.2 | Interchange support for Finale/Dorico/Sibelius. |
| **V** | SVG Engraving | ⏳ Planned v2.3 | Competitive rendering algorithms (Skyline packing, SMuFL) to rival Verovio. |
| **VI** | LSP Server | ⏳ Planned v2.4 | IDE support for VS Code/Neovim. |

---

## 🤝 Contributing

We welcome contributions, particularly in the areas of **SVG rendering algorithms** and **MusicXML schema mapping**.

1.  Read the [Tenuto Language Specification](tenuto-specification.md) to understand the `style=standard` vs `style=grid` engines.
2.  Follow the **Rust** coding standards: "Parse, don't validate".
3.  Run the test suite: `cargo test` (Includes regression tests for sticky state and tuplet math).

## 📄 License

This project is licensed under the **MIT License**. Copyright © 2026 Alec Borman and the Tenuto Working Group.
