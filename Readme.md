🎼 OmniScoreThe Semantic Compression Standard for Music Notation & AI.OmniScore is a declarative, domain-specific language (DSL) designed to describe musical logic, notation, and performance data. Unlike visual-first formats (MusicXML/PDF), OmniScore prioritizes musical intent, utilizing a "Sticky State" inference engine to calculate layout at render-time.⚡ The OmniScore Advantage: "Semantic Compression"OmniScore is built on the philosophy of Inference Over Redundancy. By stripping away layout coordinates and boilerplate, we achieve a level of compression that makes full symphonic scores readable by both humans and Large Language Models (LLMs).The "Hello World" Comparison (C Major Scale)To represent a 4-note sequence (C4 D4 E4 F4 quarter notes):FormatCode ExampleCharactersReadabilityMusicXML<note><pitch><step>C... (40+ lines)~4500%OmniScorec4:4 d e f10100%Why it matters: A full Beethoven symphony in MusicXML exceeds the context window of most AI models. In OmniScore, that same symphony fits into a single prompt, enabling AI-driven orchestration, transposition, and analysis.🚀 Quick StartA valid OmniScore file follows a strict three-part sequence: Meta, Definitions, and Flow.omniscore
  %% 1. Metadata (Global Settings)
  meta { title: "Simple Song", tempo: 120, time: 4/4 }

  %% 2. Definitions (The Physics of the Staves)
  def vln "Violin" style=standard clef=treble
  def gtr "Guitar" style=tab tuning=guitar_std

  %% 3. Flow (The Logic)
  measure 1
    vln: c4:4 d e f |
    gtr: 0-6:4 2-5 3-5 5-5 |
🛠 Core EnginesOmniScore uses distinct "Engines" to interpret data based on the instrument's physics.1. Standard Engine (style=standard)The default engine for pitched instruments.Scientific Pitch Notation: Uses [Step][Accidental][Octave] (e.g., c#4).Sticky Attributes: Once a duration (:4) or octave (4) is set, it persists until changed.Chords: Denoted with brackets [c4 e4 g4]:2.2. Tablature Engine (style=tab)For fretted instruments using a [Fret]-[String] coordinate system.Techniques: Includes .bu(interval) (Bends), .sl (Slides), and .h/.p (Legato).Tuning: Supports standard and custom arrays (e.g., tuning=[D1, A1, D2, G2]).3. Grid Engine (style=grid)For unpitched percussion or rhythmic triggers.Mapping: Maps keys to staff lines via the map object: map={ k:0, s:4, h:8 }.Modifiers: .ghost (Parentheses), .flam (Grace notes), .roll (Tremolo).📚 Technical Specification (v1.1.0)1. Rhythm & TimeSyntaxEquivalentDescription:4♩Quarter Note:8.♪.Dotted Eighth:2..𝅗𝅥..Double Dotted Half(c d e):3/23-tupleStandard Triplet2. Advanced Polyphony (Voice Groups)Handle multi-threaded logic (e.g., piano hands or choral parts) within a single staff using {}.sax: {
  v1: c5:4 d5 e5 f5 | %% Voice 1 (Up-stem)
  v2: e4:1           | %% Voice 2 (Down-stem)
}
3. Structure & Flow ControlOmniScore handles non-linear progression via explicit tokens:Repeats: |: (Start), :| (End), :|: (Double).Voltas: [1. events ... ] and [2. events ... ].Navigation: segno, coda, D.S. al Coda, Fine.4. Playback & Synth EngineOmniScore drives audio synthesis directly via patch assignments and mixer attributes.Patches: def pno "Piano" patch="Acoustic Grand Piano".Automation: vln.vol: 80, vln.pan: -64.MIDI CC: c4:1.cc(11, [0, 100]) (Expression swell).5. Macros & VariablesReduce redundancy using text-substitution macros.macro LickA = { c4:16 d eb f g f eb d }
measure 1
  gtr: $LickA $LickA+2 | %% Macro with transposition
6. MicrotonalitySupports non-12TET systems natively.Accidentals: qs (Quarter Sharp), qf (Quarter Flat).Cent Deviations: c4+14:4 (C4 tuned 14 cents sharp).🎨 Visual Styling (The Theme Engine)The visual layer is separated from musical data.Themes: meta { theme: "jazz" } (Handwritten) or standard (Classical).Overrides: event.red (Coloring), event.head("x") (Ghost/Percussive heads).🤖 AI Vision & OMR IntegrationOmniScore is the ideal target format for Optical Music Recognition (OMR). Because it maps logical intent rather than visual pixels, AI models can transcribe complex sheet music photos into OmniScore with significantly higher accuracy than MusicXML.📄 Formal Grammar (EBNF)Program         ::= 'omniscore' MetaBlock? DefBlock+ MeasureBlock+
MetaBlock       ::= 'meta' '{' KeyValuePair (',' KeyValuePair)* '}'
DefBlock        ::= 'def' Identifier StringLiteral Attribute*
MeasureBlock    ::= 'measure' MeasureRange MetaBlock? StaffLogic*
StaffLogic      ::= Identifier ':' (Event | BarLine | VoiceGroup)+
Event           ::= (Note | Chord | Rest) Duration? Modifier*
📝 Reference Exampleomniscore
  meta { title: "OmniScore Reference", tempo: 130, theme: "Jazz" }

  def sax "Tenor Sax" style=standard transpose=-14
  def gtr "Guitar"    style=tab      tuning=guitar_std
  def drm "Drum Kit"  style=grid     map=gm_standard

  measure 1
    meta { time: 4/4 }
    sax: c4:4.accent e g c5.stacc |
    gtr: [0-6 2-5 2-4]:4.down [0-6 2-5 2-4].up r:2 |
    drm: k:8. s:16 k:8 s k s k s:4.roll |
🛠 Contributing & ImplementationCompilers must maintain a state machine to track "Sticky" attributes and validate VoiceSyncError during linearization. For the full developer roadmap, see the Implementation Guidelines.License: MITMaintained by: The OmniScore Working Group
