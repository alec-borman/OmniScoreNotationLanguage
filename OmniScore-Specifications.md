omniscore
  meta { 
    title: "The Cosmic Butter Dish"
    subtitle: "Grand Sonata for Two Hands and One Existential Crisis"
    composer: "A. I. Mozart (v2.0)"
    copyright: "Copyleft 3025 - No humans were harmed in the making of this file"
    tempo: 60
    style: "Post-Post-Modern"
  }

  %% =================================================================
  %% DEFINITIONS: The Physics of the Joke
  %% =================================================================
  
  group "Steinway Model D" symbol=brace {
    %% Using specific patch names for the synth engine
    def rh "Right Hand" style=standard clef=treble patch="Acoustic Grand Piano"
    def lh "Left Hand"  style=standard clef=bass   patch="Acoustic Grand Piano"
  }

  %% MACROS: Reusable motifs of anxiety
  macro PanicRun = { c5:32 d e f g a b c6 b5 a g f e d }
  macro DjentChug = { [c1 g1 c2]:16.head("x").sfz r:16 [c1 g1 c2].head("x") }
  macro SerialRow = { c4:16 cs d ds e f fs g gs a as b } %% 12-tone row

  %% =================================================================
  %% I. THE AWAKENING (Inference Engine Demo)
  %% =================================================================
  
  measure 1
    meta { time: 5/4 }
    instruction "Lento, with the heavy burden of consciousness"
    
    %% Sticky attributes: Duration :1 (Whole note) persists for the chords
    lh: c2:1.pp g2 c3 e3 r:4 |
    
    %% Lyrics used as internal monologue, mapped 1-to-1 with notes
    rh: r:1 c5:4.fermata |
    rh.lyric: "Why? _"

  measure 2
    instruction "Realizing you exist"
    lh: f1:1.mp c2 f2 a2 r:4 |
    rh: r:1 [f4 a4 c5]:4.arp(up) |
    rh.lyric: "Oh. No."

  %% =================================================================
  %% II. THE PANIC (Polyphony & Macro Demo)
  %% =================================================================

  measure 3
    meta { time: 7/8, tempo: 174 }
    instruction "Presto, like you left the oven on"
    
    %% Complex Voice Splitting: v1 does fast runs, v2 does stabs
    rh: {
      v1: $PanicRun $PanicRun $PanicRun $PanicRun | %% 32nd notes (Macros)
      v2: c5:4.accent r:8 c5:4 |                    %% Quarter notes
    }
    
    %% Left hand doing a difficult asymmetric groove (2+2+3)
    lh: c3:8.stacc c3 c3 c3 c3 c3 c3 | 
    
    rh.lyric: "Run run run run run run run"

  measure 4
    %% Transposing the macro up a perfect 5th (+7 semitones)
    rh: {
      v1: $PanicRun+7 $PanicRun+7 $PanicRun+7 $PanicRun+7 |
      v2: g5:4.accent r:8 g5:4 |
    }
    lh: g3:8.stacc g3 g3 g3 g3 g3 g3 |
    rh.lyric: "Hide hide hide hide hide hide hide"

  %% =================================================================
  %% III. THE PRETENSION (Microtonality Demo)
  %% =================================================================

  measure 5
    meta { time: 4/4, tempo: 60 }
    instruction "Rubato, Smug Jazz Face required"
    
    %% Precise Cent Deviations for that "Out of Tune" Jazz feel
    %% C Major chord: E flat by 14 cents, G sharp by 20 cents
    rh: [c4 e4-14 g4+20 c5]:1.roll.mp |
    lh: c2:2 g2 |
    rh.lyric: "Spi- cy. _"

  measure 6
    instruction "With unearned confidence"
    %% D Minor 9, but the F is tuned 50 cents sharp (Quarter tone)
    rh: [d4 f4qs a4 c5 e5]:1.fermata |
    lh: d2:2 a2 |
    rh.lyric: "Crunch- y. _"

  %% =================================================================
  %% IV. THE SERIALIST ERROR (Strict 12-Tone & Dynamics)
  %% =================================================================
  
  measure 7
    meta { time: 12/16, tempo: 120 }
    instruction "Mathematically perfect, emotionally void"
    
    %% Every note has a radically different dynamic
    rh: c5:16.pp cs.ff d.mp ds.sfz e.p f.fff fs.pp g.f gs.mp a.sfz as.p b.fff |
    lh: r:2. |
    rh.lyric: "Math is fun and not at all stress- ful wait stop"

  %% =================================================================
  %% V. THE FALSE HOPE (The "Simple" Part)
  %% =================================================================

  measure 8
    meta { time: 4/4, tempo: 60 }
    instruction "With infinite resonance"
    
    %% A single, tiny, staccato 'ping'
    rh: c6:16.stacc.pp r:16 r:8 r:2. |
    lh: r:1 |
    rh.lyric: "Boop."

  measure 9
    %% The unspoken realization that this is just Twinkle Twinkle Little Star
    meta { tempo: 120 }
    instruction "Allegro childishness"
    
    rh: c4:4 c4 g4 g4 |
    lh: c3:4 c3 e3 e3 |
    rh.lyric: "Wait, isn't this...?"

  measure 10
    instruction "Give up"
    rh: [c4 e4 g4]:1.fermata |
    lh: [c2 c3]:1.fermata |
    rh.lyric: "Yep."

  %% =================================================================
  %% VI. THE MINIMALIST VOID (Looping & Stamina)
  %% =================================================================
  
  measure 11
    instruction "Realizing the contract requires 10 minutes"
    rh: r:2 c5:8 c5 r:4 |
    rh.lyric: "Oh no."
  
  measure 12..19
    meta { time: 6/8, tempo: 160 }
    instruction "Glass-y eyed stare (Repeat ad nauseam)"
    
    %% Implicit repetition via lazy typing of 16th notes
    rh: c5:16 e g c6 g e c5 e g c6 g e |
    lh: c3:4. c2 |
    
    %% OmniScore maps syllables to notes automatically
    rh.lyric: "Art is re pe ti tion is re pe ti tion is _"

  %% =================================================================
  %% VII. THE FUGUE OF REGRET (Counterpoint)
  %% =================================================================

  measure 20
    meta { time: 2/4, tempo: 100 }
    instruction "Scholarly, dry, and dusty"
    
    %% Subject entry in RH
    rh: c5:8 g4 e4 c4 |
    lh: r:2 |
    rh.lyric: "I am a fugue."

  measure 21
    %% Answer in LH, Counter-subject in RH
    rh: d5:16 e f d g4:8 g |
    lh: g3:8 d3 b2 g2 |
    lh.lyric: "I am al- so a fugue."
    rh.lyric: "Look at the coun- ter- point."

  %% =================================================================
  %% VIII. THE DJENT BREAKDOWN (Percussive Piano)
  %% =================================================================
  
  measure 22
    meta { time: 4/4, tempo: 90 }
    instruction "Reach inside and mute the strings manually"
    
    %% Using percussive noteheads on pitched staff
    %% Low C octaves slammed with force using the DjentChug macro
    lh: $DjentChug r:8 [c1 g1 c2]:8.head("x") [c1 g1 c2]:4.head("x").accent |
    rh: r:1 |
    lh.lyric: "CHUG CHUG _ CHUG"

  measure 23
    instruction "Polyrhythmic confusion"
    lh: $DjentChug $DjentChug |
    rh: r:4 [c5 e5 g5]:2.head("x").sfz r:4 | %% Random stab
    lh.lyric: "CHUG CHUG CHUG CHUG"
    rh.lyric: "AH!"

  %% =================================================================
  %% IX. THE LISZT SIMULATOR (Arpeggiation & Tuplets)
  %% =================================================================

  measure 24
    meta { time: 12/8, tempo: 80 }
    instruction "With excessive hair tossing"
    
    %% A massive tuple run: 23 notes in the time of 1 dotted quarter (virtually)
    rh: (c4 d e f g a b c5 d e f g a b c6 d e f g a b c7):23/4.ff |
    lh: [c2 c3]:1.tremolo |
    
    rh.lyric: "Look- at- me- I- am- so- fast- and- ro- man- tic"

  measure 25
    instruction "Faux-profundity"
    rh: [c4 eb4 g4 bb4 d5]:1.fermata.arp(up) |
    rh.lyric: "Sigh."

  %% =================================================================
  %% X. THE FINAL RESOLUTION (Or is it?)
  %% =================================================================

  measure 26
    meta { time: 4/4, tempo: 60 }
    instruction "Adagio for Strings (but it's a piano)"
    
    rh: c5:2 b4:4.tr(natural) c5:8 |
    lh: a2:1 |
    rh.lyric: "Near- ly there."

  measure 27
    instruction "The actual end"
    
    %% Quarter tone resolution just to be annoying
    %% The audience expects C5 natural. We give them C5 Quarter-Sharp.
    rh: c5qs:1.fermata.pp | 
    lh: c3:1.fermata |
    
    rh.lyric: "Close e- nough."
