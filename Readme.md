<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniScore Visualizer: Mary Had a Little Lamb</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Load Tone.js for audio synthesis -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
    <style>
        .white-key {
            width: 40px;
            height: 180px;
            background: white;
            border: 1px solid #1f2937; /* Dark Gray */
            cursor: pointer;
            position: relative;
            z-index: 10;
            transition: background 0.1s ease;
        }
        .black-key {
            width: 25px;
            height: 110px;
            background: #1f2937; /* Dark Gray */
            border: 1px solid black;
            cursor: pointer;
            position: absolute;
            z-index: 20;
            margin-left: -12.5px;
            margin-right: -12.5px;
            transition: background 0.1s ease;
        }
        .key-active-white {
            background: #fca5a5; /* Red-300 */
        }
        .key-active-black {
            background: #ef4444; /* Red-500 */
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen p-4 flex flex-col items-center justify-center font-sans">

    <div class="max-w-4xl w-full bg-white shadow-xl rounded-xl p-8 space-y-6">
        <h1 class="text-3xl font-bold text-center text-gray-800">OmniScore Piano Visualizer</h1>
        <p class="text-center text-gray-600">Playing "Mary Had a Little Lamb" from the Canvas notation. The melody is played by the Right Hand.</p>

        <!-- Piano Visualization Area -->
        <div id="piano-container" class="relative overflow-x-auto p-4 bg-gray-200 rounded-lg shadow-inner">
            <div id="keyboard" class="flex justify-center mx-auto" style="width: 500px;">
                <!-- Keys will be generated here -->
            </div>
        </div>

        <!-- Controls -->
        <div class="flex justify-center space-x-4">
            <button id="playButton" class="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed">
                Play Melody
            </button>
            <button id="stopButton" class="px-6 py-3 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed" disabled>
                Stop
            </button>
        </div>

        <!-- Status Message -->
        <div id="status" class="text-center text-sm text-gray-500 mt-4">Click 'Play Melody' to start.</div>

        <!-- Source OmniScore -->
        <div class="mt-8">
            <h2 class="text-xl font-semibold text-gray-700">Source OmniScore (Right Hand Melody):</h2>
            <pre id="omni-code" class="bg-gray-800 text-green-300 p-4 rounded-lg text-sm overflow-x-auto"></pre>
        </div>
    </div>

    <script>
        const omniScoreCode = `
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
  rh: e4:4 d4:4 c4:4 d4:4 |  // E-D-C-D (Quarter notes)
  lh: c3:1                |  // C Major chord root (Whole note)
measure 2
  rh: e4:4 e4:4 e4:2 r:2  |  // E-E-E (Quarter notes, followed by a rest)
  lh: c3:1                |  // C Major chord root (Whole note)
measure 3
  rh: d4:4 d4:4 d4:2 r:2  |  // D-D-D (Quarter notes, followed by a rest)
  lh: g3:1                |  // G Major chord root (Whole note)
measure 4
  rh: e4:4 g4:4 g4:2 r:2  |  // E-G-G (Quarter notes, followed by a rest)
  lh: c3:1                |  // C Major chord root (Whole note)

// --- SECTION B ---
// Its fleece was white as snow
measure 5
  rh: e4:4 d4:4 c4:4 d4:4 |  // E-D-C-D (Quarter notes)
  lh: c3:1                |  // C Major chord root (Whole note)
measure 6
  rh: e4:4 e4:4 e4:4 e4:4 |  // E-E-E-E (Four Quarter notes)
  lh: f3:1                |  // F Major chord root (Whole note)
measure 7
  rh: d4:4 d4:4 e4:4 d4:4 |  // D-D-E-D (Quarter notes)
  lh: g3:1                |  // G Major chord root (Whole note)
measure 8
  rh: c4:1                |  // C (Whole note - the end!)
  lh: c3:1                |  // C Major chord root (Whole note)
`;
        
        document.getElementById('omni-code').textContent = omniScoreCode;

        const playButton = document.getElementById('playButton');
        const stopButton = document.getElementById('stopButton');
        const statusDiv = document.getElementById('status');
        const keyboardDiv = document.getElementById('keyboard');

        let isPlaying = false;
        let scheduledEvents = [];

        // --- Tone.js Setup ---
        const synth = new Tone.Synth().toDestination();
        const tempo = 100; // BPM
        const beatDuration = 60 / tempo; // seconds per beat

        // Map OmniScore duration fractions to Tone.js friendly durations (seconds)
        const durationMap = {
            '1': 4 * beatDuration, // Whole note (4 beats)
            '2': 2 * beatDuration, // Half note (2 beats)
            '4': 1 * beatDuration, // Quarter note (1 beat)
            '8': 0.5 * beatDuration, // Eighth note (0.5 beats)
            // Dotted notes are not used in this score, but could be calculated
        };

        const notes = [
            'c4', 'd4', 'e4', 'f4', 'g4', // Notes used in the melody
        ];

        const allKeys = [
            'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',
            'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',
            'C5'
        ];
        
        const whiteKeys = allKeys.filter(k => k.length === 2);
        const blackKeys = allKeys.filter(k => k.length === 3);

        // --- Keyboard Visualization Functions ---

        function createKeyboard() {
            keyboardDiv.innerHTML = '';
            const fragment = document.createDocumentFragment();
            
            // Focus on the C4-G4 range used in the melody, plus surrounding notes for context
            const displayedWhiteKeys = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'];
            let offset = 0;

            for (let i = 0; i < displayedWhiteKeys.length; i++) {
                const keyName = displayedWhiteKeys[i];
                const key = document.createElement('div');
                key.className = 'white-key rounded-b-md flex flex-col justify-end items-center text-xs font-bold text-gray-700';
                key.id = 'key-' + keyName.toLowerCase();
                key.style.marginLeft = (keyName.startsWith('F') || keyName.startsWith('C') ? '0' : '-1px');
                
                // Add the note label
                const label = document.createElement('span');
                label.textContent = keyName;
                label.className = 'mb-2';
                key.appendChild(label);
                
                fragment.appendChild(key);

                // Add black keys
                if (keyName !== 'E4' && keyName !== 'B4' && keyName !== 'C5') {
                    // Determine the sharp key name (e.g., C4 becomes C#4)
                    const sharpKeyName = keyName.charAt(0) + '#' + keyName.charAt(1);
                    const sharpKey = document.createElement('div');
                    sharpKey.className = 'black-key rounded-b-md';
                    sharpKey.id = 'key-' + sharpKeyName.toLowerCase();
                    
                    // Position the black key over the joint of the two white keys
                    const whiteKeyWidth = 40;
                    const blackKeyWidth = 25;
                    // Position relative to the parent (keyboardDiv)
                    const leftPosition = offset + (whiteKeyWidth - (blackKeyWidth / 2)) - 1; // 1px border offset
                    
                    sharpKey.style.left = `${leftPosition}px`;
                    
                    // We need to place this absolute positioned key in the right spot relative to the white keys.
                    // This is complex in a simple flex container, so we'll use a wrapper div.
                    // Let's simplify the placement using CSS grid or absolute positioning relative to a fixed-width container.

                    // Since we're using flex, let's use margins to shift the black keys back.
                    // Instead of positioning absolutely in a flex container, let's just create the keys first, then position.
                }
                offset += whiteKeyWidth;
            }

            // Simple placement for this short scale, using absolute positioning relative to the keyboardDiv's center
            keyboardDiv.style.position = 'relative';
            keyboardDiv.style.display = 'flex';
            keyboardDiv.style.justifyContent = 'center';
            keyboardDiv.style.height = '200px';

            const whiteKeyNames = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'];
            const blackKeyNames = ['C#4', 'D#4', 'F#4', 'G#4', 'A#4'];
            const startX = -190; // Starting X position for the whole keyboard to center it

            // Helper to create and append a key
            const appendKey = (name, isBlack, xPos) => {
                const key = document.createElement('div');
                key.id = 'key-' + name.toLowerCase().replace('#', 's');
                key.style.position = 'absolute';
                key.style.left = `calc(50% + ${xPos}px)`;

                if (isBlack) {
                    key.className = 'black-key rounded-b-md';
                    key.style.height = '120px'; // Taller black key
                } else {
                    key.className = 'white-key rounded-b-md flex flex-col justify-end items-center text-xs font-bold text-gray-700';
                    key.style.height = '180px'; // Standard height
                    const label = document.createElement('span');
                    label.textContent = name.replace('s', '#');
                    label.className = 'mb-2';
                    key.appendChild(label);
                }
                keyboardDiv.appendChild(key);
                return key;
            };

            let currentX = startX;
            let blackKeyIndex = 0;

            for (let i = 0; i < whiteKeyNames.length; i++) {
                const name = whiteKeyNames[i];
                appendKey(name, false, currentX);

                if (name !== 'E4' && name !== 'B4' && blackKeyIndex < blackKeyNames.length) {
                    // Place sharp key
                    // Position it 3/4 of the way across the current white key
                    const sharpX = currentX + 40 - 12.5; 
                    appendKey(blackKeyNames[blackKeyIndex], true, sharpX);
                    blackKeyIndex++;
                }

                currentX += 40; // Move to the start of the next white key
            }
        }

        // --- OmniScore Parsing ---
        function parseOmniScore(code) {
            const melody = [];
            const rhPattern = /rh:\s*([^|]+)/g;
            const noteDurationRegex = /([a-g][#b]?\d|r):(\d\.\d|\d\.)|([a-g][#b]?\d|r):(\d)/g;
            let currentTime = 0;

            // This is a highly simplified parser targeting ONLY the 'rh' line
            let match;
            while ((match = rhPattern.exec(code)) !== null) {
                const notesString = match[1].trim();
                let noteMatch;

                while ((noteMatch = noteDurationRegex.exec(notesString)) !== null) {
                    const note = noteMatch[1] || noteMatch[3];
                    const durationStr = noteMatch[2] || noteMatch[4];
                    
                    if (!durationMap[durationStr]) {
                        console.warn('Unknown duration format:', durationStr);
                        continue;
                    }
                    
                    const duration = durationMap[durationStr];

                    melody.push({
                        note: note.toUpperCase(), // Tone.js prefers C4, D4 format
                        duration: duration,
                        time: currentTime
                    });
                    
                    currentTime += duration;
                }
            }

            return melody;
        }

        // --- Scheduling and Playback ---

        function playMelody(parsedMelody) {
            if (isPlaying) return;

            Tone.Transport.stop();
            Tone.Transport.cancel(0);
            scheduledEvents = [];
            isPlaying = true;
            statusDiv.textContent = 'Playing...';
            playButton.disabled = true;
            stopButton.disabled = false;
            
            // Highlight off all keys
            document.querySelectorAll('.white-key, .black-key').forEach(key => {
                key.classList.remove('key-active-white', 'key-active-black');
            });
            
            // Schedule the notes
            parsedMelody.forEach(item => {
                if (item.note === 'R') {
                    // Skip rests but advance time
                    return;
                }
                
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
                }, item.time + item.duration - 0.05); // Use a small offset
                scheduledEvents.push(visualOffEvent);
            });
            
            // Schedule stop/cleanup at the very end
            const totalDuration = parsedMelody[parsedMelody.length - 1].time + parsedMelody[parsedMelody.length - 1].duration;
            const endEvent = Tone.Transport.schedule(stopPlayback, totalDuration);
            scheduledEvents.push(endEvent);


            Tone.Transport.start();
        }
        
        function stopPlayback() {
            if (!isPlaying) return;
            
            Tone.Transport.stop();
            Tone.Transport.cancel(0);
            
            isPlaying = false;
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
            createKeyboard();

            playButton.addEventListener('click', async () => {
                if (Tone.Transport.state !== 'started') {
                    await Tone.start();
                    Tone.Context.lookAhead = 0.1; // Reduce latency
                }
                try {
                    const parsedMelody = parseOmniScore(omniScoreCode);
                    playMelody(parsedMelody);
                } catch (error) {
                    statusDiv.textContent = 'Error parsing score: ' + error.message;
                    console.error('Parsing/Playback Error:', error);
                    stopPlayback();
                }
            });

            stopButton.addEventListener('click', stopPlayback);
        }

    </script>
</body>
</html>
