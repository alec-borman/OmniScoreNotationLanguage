<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniScore Visualizer: Custom Editor</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Load Tone.js for audio synthesis -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
    <style>
        /* General key styling */
        .white-key, .black-key {
            cursor: pointer;
            position: absolute;
            transition: background 0.1s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        /* White key specifics */
        .white-key {
            width: 40px;
            height: 180px;
            background: white;
            border: 1px solid #1f2937; /* Dark Gray */
            z-index: 10;
        }
        /* Black key specifics */
        .black-key {
            width: 25px;
            height: 120px;
            background: #1f2937; /* Dark Gray */
            z-index: 20;
            /* Black keys are centered over the join of the two white keys */
        }
        /* Active states for highlighting */
        .key-active-white {
            background: #fca5a5; /* Red-300 */
            box-shadow: 0 0 10px #f87171;
        }
        .key-active-black {
            background: #ef4444; /* Red-500 */
            box-shadow: 0 0 10px #ef4444;
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen p-4 flex flex-col items-center justify-center font-sans">

    <div class="max-w-4xl w-full bg-white shadow-xl rounded-xl p-8 space-y-6">
        <h1 class="text-3xl font-bold text-center text-gray-800">OmniScore Piano Visualizer & Editor (C3 to C6)</h1>
        <p class="text-center text-gray-600">The keyboard now spans 3 octaves (C3 to C6) and uses a more realistic piano sound.</p>

        <!-- Piano Visualization Area - Wider for C3 to C6 -->
        <div id="piano-container" class="relative overflow-x-auto p-4 bg-gray-200 rounded-lg shadow-inner">
            <div id="keyboard" class="relative mx-auto" style="height: 200px;">
                <!-- Keys will be generated here -->
            </div>
        </div>

        <!-- Controls -->
        <div class="flex justify-center space-x-4">
            <button id="playButton" class="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed">
                Play Full Score
            </button>
            <button id="stopButton" class="px-6 py-3 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed" disabled>
                Stop
            </button>
        </div>

        <!-- Status Message -->
        <div id="status" class="text-center text-sm text-gray-500 mt-4 h-6">Click 'Play Full Score' to start.</div>

        <!-- Editable OmniScore Input -->
        <div class="mt-8">
            <h2 class="text-xl font-semibold text-gray-700 mb-2">Edit Your OmniScore Here:</h2>
            <textarea id="omni-input" class="w-full h-64 bg-gray-800 text-green-300 p-4 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-y"></textarea>
        </div>
    </div>

    <script>
        // Initial score is defined here to populate the textarea
        const initialOmniScoreCode = `
meta {
  title: "Mary Had a Little Lamb"
  composer: "Traditional (OmniScore Arrangement)"
}

group "Piano" symbol=brace {
  def rh "Melody (Right Hand)" style=standard clef=treble
  def lh "Chords (Left Hand)"  style=standard clef=bass
}
// Time Signature: 4 beats per measure (4/4 time)
// Tempo: 100 beats per minute (Moderato)
meta { time: 4/4, tempo: 100 }

// --- SECTION A ---
// Mary had a little lamb
measure 1
  rh: e4:4 d4:4 c4:4 d4:4 |  // E-D-C-D (4 Quarter notes = 4 beats)
  lh: c3:1                |  // C Major chord root (Whole note = 4 beats)
measure 2
  rh: e4:4 e4:4 e4:2      |  // E-E-E (Quarter, Quarter, Half = 4 beats)
  lh: c3:1                |  // C Major chord root (Whole note)
measure 3
  rh: d4:4 d4:4 d4:2      |  // D-D-D (Quarter, Quarter, Half = 4 beats)
  lh: g3:1                |  // G Major chord root (Whole note)
measure 4
  rh: e4:4 g4:4 g4:2      |  // E-G-G (Quarter, Quarter, Half = 4 beats)
  lh: c3:1                |  // C Major chord root (Whole note)

// --- SECTION B ---
// Its fleece was white as snow
measure 5
  rh: e4:4 d4:4 c4:4 d4:4 |  // E-D-C-D (4 Quarter notes)
  lh: c3:1                |  // C Major chord root (Whole note)
measure 6
  rh: e4:4 e4:4 e4:4 e4:4 |  // E-E-E-E (Four Quarter notes)
  lh: f3:1                |  // F Major chord root (Whole note)
measure 7
  rh: d4:4 d4:4 e4:4 d4:4 |  // D-D-E-D (Four Quarter notes)
  lh: g3:1                |  // G Major chord root (Whole note)
measure 8
  rh: c4:1                |  // C (Whole note - the end!)
  lh: c3:1                |  // C Major chord root (Whole note)
`;
        
        const playButton = document.getElementById('playButton');
        const stopButton = document.getElementById('stopButton');
        const statusDiv = document.getElementById('status');
        const keyboardDiv = document.getElementById('keyboard');
        const omniInput = document.getElementById('omni-input'); // Reference to the textarea

        let isPlaying = false;
        let scheduledEvents = [];

        // --- Tone.js Setup ---
        // Changed to Tone.PolySynth and adjusted envelope for a more piano-like, percussive sound
        const synth = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: "sawtooth" }, // Richer waveform than triangle
            envelope: {
                attack: 0.002, // Very fast attack
                decay: 0.4,    // Medium decay
                sustain: 0.05, // Very low sustain (quickly fades)
                release: 0.8   // Longer release
            }
        }).toDestination();
        
        const tempo = 100; // BPM 
        const beatDuration = 60 / tempo; // seconds per beat

        // Map OmniScore duration fractions to Tone.js friendly durations (seconds)
        const durationMap = {
            '1': 4 * beatDuration, // Whole note (4 beats)
            '2': 2 * beatDuration, // Half note (2 beats)
            '4': 1 * beatDuration, // Quarter note (1 beat)
            '8': 0.5 * beatDuration, // Eighth note (0.5 beats)
        };

        // --- Keyboard Visualization Functions ---

        function createKeyboard() {
            // EXPANDED: Displayed range is now 3 octaves: C3 to C6
            const whiteKeyNames = [
                'C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'B3',
                'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4',
                'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5',
                'C6' 
            ];
            const blackKeyNames = [
                'C#3', 'D#3', 'F#3', 'G#3', 'A#3',
                'C#4', 'D#4', 'F#4', 'G#4', 'A#4',
                'C#5', 'D#5', 'F#5', 'G#5', 'A#5'
            ];
            
            const whiteKeyWidth = 40;
            const keyboardWidth = whiteKeyNames.length * whiteKeyWidth; // 22 * 40 = 880px
            const blackKeyWidth = 25;

            keyboardDiv.style.width = `${keyboardWidth}px`; // Set explicit width
            keyboardDiv.innerHTML = ''; // Clear existing content

            let currentX = 0; // Start at 0
            let blackKeyIndex = 0;

            // Helper to create and append a key
            const appendKey = (name, isBlack, xPos) => {
                const key = document.createElement('div');
                // Use 's' for sharp as a safe ID character (e.g., C#4 -> Cs4)
                key.id = 'key-' + name.toLowerCase().replace('#', 's');
                key.style.position = 'absolute';
                key.style.left = `${xPos}px`;
                key.style.zIndex = isBlack ? 20 : 10;

                if (isBlack) {
                    key.className = 'black-key rounded-b-md';
                } else {
                    key.className = 'white-key rounded-b-md flex flex-col justify-end items-center text-xs font-bold text-gray-700';
                    const label = document.createElement('span');
                    label.textContent = name;
                    label.className = 'mb-2';
                    key.appendChild(label);
                }
                keyboardDiv.appendChild(key);
            };

            for (let i = 0; i < whiteKeyNames.length; i++) {
                const name = whiteKeyNames[i];
                
                // 1. Append White Key
                appendKey(name, false, currentX);

                // 2. Append Black Key (if applicable)
                // Black keys exist between C-D, D-E, F-G, G-A, A-B
                if (name.includes('C') || name.includes('D') || name.includes('F') || name.includes('G') || name.includes('A')) {
                    // Check if we still have sharp keys to append in the blackKeyNames array
                    if (blackKeyIndex < blackKeyNames.length) {
                        // Position the sharp key centered over the split
                        const sharpX = currentX + (whiteKeyWidth - (blackKeyWidth / 2)); 
                        appendKey(blackKeyNames[blackKeyIndex], true, sharpX);
                        blackKeyIndex++;
                    }
                }

                currentX += whiteKeyWidth; // Move to the start of the next white key
            }
        }

        // --- OmniScore Parsing ---
        function parseOmniScore(code) {
            const events = [];
            // Target both Right Hand (rh) and Left Hand (lh)
            const parts = [
                { hand: 'RH', pattern: /rh:\s*([^|]+)/g },
                { hand: 'LH', pattern: /lh:\s*([^|]+)/g }, 
            ];
            
            // Regex to capture Note/Rest (e.g., e4 or r) and Duration (e.g., 4 or 1)
            // It handles fractional durations (group 2) OR integer durations (group 4)
            const noteDurationRegex = /([a-g][#b]?\d|r):(\d\.\d|\d\.)|([a-g][#b]?\d|r):(\d)/g;

            parts.forEach(part => {
                let currentTime = 0;
                // Reset regex position before reuse
                part.pattern.lastIndex = 0; 
                
                let measureMatch;
                while ((measureMatch = part.pattern.exec(code)) !== null) {
                    const notesString = measureMatch[1].trim();
                    let noteMatch;

                    // Reset regex position before reuse for inner loop
                    noteDurationRegex.lastIndex = 0;

                    while ((noteMatch = noteDurationRegex.exec(notesString)) !== null) {
                        const note = noteMatch[1] || noteMatch[3]; // Note or Rest (r)
                        const durationStr = noteMatch[2] || noteMatch[4]; // Duration string (e.g., '4' or '1')
                        
                        const duration = durationMap[durationStr];
                        if (!duration) {
                            // Throw error for user-visible feedback on invalid input
                            throw new Error(`Invalid duration '${durationStr}' found for note ${note}. Please use '1', '2', '4', or '8'.`);
                        }

                        events.push({
                            note: note.toUpperCase(), // Tone.js prefers C4, D4 format
                            duration: duration,
                            time: currentTime,
                            hand: part.hand
                        });
                        
                        currentTime += duration;
                    }
                }
            });

            // CRITICAL: Sort events chronologically to interleave RH and LH notes correctly
            events.sort((a, b) => a.time - b.time);

            return events;
        }

        // --- Scheduling and Playback ---

        function playScore(parsedEvents) {
            if (isPlaying) return;

            Tone.Transport.stop();
            Tone.Transport.cancel(0);
            scheduledEvents = [];
            isPlaying = true;
            statusDiv.className = 'text-center text-sm text-blue-600 mt-4 h-6';
            statusDiv.textContent = 'Playing Full Score...';
            playButton.disabled = true;
            stopButton.disabled = false;
            
            // Highlight off all keys
            document.querySelectorAll('.white-key, .black-key').forEach(key => {
                key.classList.remove('key-active-white', 'key-active-black');
            });
            
            // Schedule the notes
            parsedEvents.forEach(item => {
                if (item.note === 'R') {
                    return; // Skip rests
                }
                
                // Get the consistent key ID (C#4 becomes Cs4)
                const noteId = 'key-' + item.note.toLowerCase().replace('#', 's');
                const keyElement = document.getElementById(noteId);
                const isBlack = item.note.includes('#');
                const activeClass = isBlack ? 'key-active-black' : 'key-active-white';
                
                // 1. Schedule the Note Playback
                const noteEvent = Tone.Transport.schedule(time => {
                    synth.triggerAttackRelease(item.note, item.duration, time);
                }, item.time);
                scheduledEvents.push(noteEvent);

                // 2. Schedule the Visual On state
                const visualOnEvent = Tone.Transport.schedule(time => {
                    if (keyElement) {
                        Tone.Draw.schedule(() => {
                            keyElement.classList.add(activeClass);
                        }, time);
                    }
                }, item.time);
                scheduledEvents.push(visualOnEvent);
                
                // 3. Schedule the Visual Off state (slightly before the next note/end of duration)
                const visualOffEvent = Tone.Transport.schedule(time => {
                    if (keyElement) {
                        Tone.Draw.schedule(() => {
                            keyElement.classList.remove(activeClass);
                        }, time);
                    }
                }, item.time + item.duration - 0.05); 
                scheduledEvents.push(visualOffEvent);
            });
            
            // Schedule stop/cleanup at the very end
            const lastEvent = parsedEvents[parsedEvents.length - 1];
            let totalDuration = 0;
            if (lastEvent) {
                // Determine the end time of the score
                totalDuration = lastEvent.time + lastEvent.duration;
            }
            
            const endEvent = Tone.Transport.schedule(stopPlayback, totalDuration);
            scheduledEvents.push(endEvent);


            Tone.Transport.start();
        }
        
        function stopPlayback() {
            if (!isPlaying) return;
            
            Tone.Transport.stop();
            Tone.Transport.cancel(0);
            
            isPlaying = false;
            statusDiv.className = 'text-center text-sm text-gray-500 mt-4 h-6';
            statusDiv.textContent = 'Ready to play.';
            playButton.disabled = false;
            stopButton.disabled = true;

            // Remove all visual highlights
            document.querySelectorAll('.white-key, .black-key').forEach(key => {
                key.classList.remove('key-active-white', 'key-active-black');
            });
        }
        
        // --- Initialization ---

        window.onload = function() {
            // 1. Populate the editor with the initial score
            omniInput.value = initialOmniScoreCode.trim();

            // 2. Build the keyboard
            createKeyboard();

            // 3. Attach event listeners
            playButton.addEventListener('click', async () => {
                // Read score from the editor
                const currentOmniScoreCode = omniInput.value;

                // Initialize Tone.js only if necessary
                if (Tone.Transport.state !== 'started') {
                    await Tone.start();
                    Tone.Context.lookAhead = 0.1; // Reduce latency
                }
                
                // Stop any previous playback
                stopPlayback(); 

                try {
                    // Attempt to parse the user's input
                    const parsedEvents = parseOmniScore(currentOmniScoreCode);
                    
                    if (parsedEvents.length === 0) {
                        statusDiv.className = 'text-center text-sm text-orange-600 mt-4 h-6';
                        statusDiv.textContent = 'Warning: No musical notes found in the score.';
                        return;
                    }
                    
                    // If parsing succeeds, play the score
                    playScore(parsedEvents);

                } catch (error) {
                    // Show parsing errors to the user
                    statusDiv.className = 'text-center text-sm text-red-600 mt-4 h-6';
                    statusDiv.textContent = 'Parsing Error: ' + error.message;
                    console.error('Parsing/Playback Error:', error);
                    stopPlayback(); // Ensure everything is stopped on error
                }
            });

            stopButton.addEventListener('click', stopPlayback);
        }

    </script>
</body>
</html>
