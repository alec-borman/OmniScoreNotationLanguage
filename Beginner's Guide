Markdown

## 🎹 Step 1: Set Up the Music File (Header and Definitions)

This section creates the basic structure and defines the instruments.

* Use `meta` and curly brackets `{}` to define the song's information.
* Use `group` and `def` to define the **Piano** and its two voices (**Right Hand** and **Left Hand**).

meta { title: "My First OmniScore Song" composer: "My Name" }

group "Piano" symbol=brace { def rh "Right Hand" style=standard clef=treble // Higher notes def lh "Left Hand" style=standard clef=bass // Lower notes }


---

## ⏱️ Step 2: Define the Starting Rules (Time and Tempo)

This sets the rhythm and speed for the entire piece.

* `time: 4/4` means 4 beats per measure.
* `tempo: 80` means 80 beats per minute.

meta { time: 4/4, tempo: 80 }


---

## 🎵 Step 3: Define the Notes (Pitch, Octave, and Duration)

Every note requires a **Pitch**, an **Octave**, and a **Duration**.

### A. Pitch and Octave

Use the letter (A-G) and a number (1-8).

| Note Name | Meaning |
| :--- | :--- |
| **`c4`** | **Middle C** (The central C). |
| **`e4`** | E above Middle C. |
| **`c3`** | C below Middle C. |
| **`f#4`** | F-sharp above Middle C. |
| **`eb4`** | E-flat above Middle C. |

### B. Duration

Use a colon `:` followed by a number that indicates the fraction of a whole note.

| Musical Note | Code | Beats (in 4/4 time) |
| :--- | :--- | :--- |
| **Whole Note** | `:1` | 4 beats |
| **Half Note** | `:2` | 2 beats |
| **Quarter Note** | `:4` | 1 beat |
| **Eighth Note** | `:8` | $1/2$ beat |
| **Dotted Half Note** | `:2.` | 3 beats |

---

## 🎼 Step 4: Write the Measures (Putting it All Together)

Each musical line is inside a `measure` block. You must ensure the notes in the measure add up to the total number of beats defined in the time signature (4 beats in 4/4 time).

### A. Melody (Single Notes)

The **Right Hand (rh)** plays a simple sequence.

measure 1 rh: c4:4 d4:4 e4:4 f4:4 | // Four Quarter Notes (1 + 1 + 1 + 1 = 4 beats) lh: r:1 | // The Left Hand rests for the whole measure (r:1)


### B. Chords (Multiple Notes at Once)

Use **square brackets `[]`** to play notes simultaneously.

measure 2 rh: r:2 | // RH rests for two beats lh: [c3 e3 g3]:2 [f2 a2 c3]:2 | // LH plays two chords, each lasting 2 beats (2 + 2 = 4 beats)


### C. Complete Example

This combines all the steps above into a single, executable block of music code.

meta { title: "OmniScore Practice" composer: "Learner" } group "Piano" symbol=brace { def rh "Right Hand" style=standard clef=treble def lh "Left Hand" style=standard clef=bass } meta { time: 4/4, tempo: 80 }

measure 1 rh: c4:4 d4:4 e4:4 f4:4 | lh: c2:1 | measure 2 rh: r:2 | lh: [c3 e3 g3]:2 [f2 a2 c3]:2 | measure 3 rh: g4:1 | // A whole note G (4 beats) lh: r:1 |
