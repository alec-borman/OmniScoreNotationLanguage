# 🎹 OmniScore IDE: Installation & User Guide

Welcome to the **OmniScore Reference IDE**. This local environment provides a retro-styled terminal and a real-time oscilloscope visualizer for developing music using the OmniScore language.

This guide assumes you have downloaded and extracted the `omniscore-ide` project files.

---

## 📋 Prerequisites

Before starting, ensure you have the following installed on your computer:

1.  **Node.js** (Version 18 or higher)
    *   [Download Node.js here](https://nodejs.org/)
    *   *Verify installation by running `node -v` in your terminal.*

---

## 🚀 Part 1: Installation

### 1. Extract the Project
Unzip the downloaded project folder to a location of your choice (e.g., `~/Documents/omniscore-ide`).

### 2. Open the Terminal
Open your system's terminal (Command Prompt, PowerShell, or macOS Terminal) and navigate to the project folder:

```bash
cd path/to/omniscore-ide
```

### 3. Install Dependencies
Run the following command to download the necessary libraries (React, Vite, Tailwind, etc.):

```bash
npm install
```

### 4. Start the IDE
Launch the development server:

```bash
npm run dev
```

The terminal will display a local address, usually **`http://localhost:5173`**. Open this URL in your web browser (Chrome or Edge recommended).

---

## 🎵 Part 2: Writing Your First Score

Once the IDE is loaded in your browser, you will see the **OmniScore Shell** (`guest@omni:/usr/home/omni$`).

Follow these steps to create "Mary Had a Little Lamb" using OmniScore's "Sticky State" logic.

### 1. Create the File
In the browser terminal, type the following command to open the built-in Nano editor:

```bash
nano mary.omni
```

### 2. Enter the Music Code
You are now in the editor view. Copy and paste the code below.

> **Note:** We only specify durations (like `q` for quarter, `h` for half) when they change. The compiler remembers the last duration used.

```omniscore
// Mary Had a Little Lamb
@tempo 120

// Section 1: "Mary had a little lamb"
m1:
  E4 q D C D    // Start with Quarter notes (q)
  E E E h       // Last E is a Half note (h)

// Section 2: "Little lamb, little lamb"
m2:
  D4 q D D h    // Reset to Quarter (q), end on Half (h)
  E4 q G G h

// Section 3: "Mary had a little lamb"
m3:
  E4 q D C D    // Sticky state handles the pitch octaves
  E E E E

// Section 4: "Its fleece was white as snow"
m4:
  D D E D C w   // End on a Whole note (w)
```

### 3. Save and Exit
1.  Click the **`^O Write Out`** button at the bottom of the screen to save.
2.  Click the **`^X Exit`** button to return to the shell.

---

## 🎹 Part 3: Compiling & Visualizing

Now that the source code is saved, we will compile it into sound events and trigger the visualizer.

### 1. Verify the File
Check that your file exists by listing the directory:
```bash
ls
```
*You should see `mary.omni` in the file list.*

### 2. Run the Compiler
Execute the `omnic run` command:

```bash
omnic run mary.omni
```

### 3. The Visualization
If your code is correct:
1.  The screen will switch to the **Oscilloscope View**.
2.  **Green Bars** representing notes will scroll across the screen relative to the red playhead.
3.  **Real-time Metrics:** You will see the beat counter and event count in the top left.

> **To Exit:** Press the **`ESC`** key on your keyboard to stop playback and return to the terminal.

---

## 🛠️ Command Reference

The OmniScore Shell supports the following commands:

| Command | Usage | Description |
| :--- | :--- | :--- |
| `ls` | `ls` | List files in the virtual directory. |
| `cat` | `cat [file]` | Display the contents of a file. |
| `nano` | `nano [file]` | Open the text editor to create or modify scripts. |
| `omnic build` | `omnic build [file]` | Compile a file and show performance stats (no visualizer). |
| `omnic run` | `omnic run [file]` | Compile and launch the real-time oscilloscope. |
| `seed` | `seed [id]` | Generate a random musical score for testing. |
| `clear` | `clear` | Clear the terminal history. |
