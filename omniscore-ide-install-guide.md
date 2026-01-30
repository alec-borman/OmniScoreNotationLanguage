# 🎵 OmniScore IDE

The official reference compiler and development environment for the **OmniScore** music programming language. This IDE provides a real-time environment to write music via code, visualize it on a piano roll, and compile it into a linearized Intermediate Representation (IR).

## ✨ Features

* **Custom Compiler (`omnic`):** Lexes and parses OmniScore syntax with support for sticky durations and octaves.
* **Piano Roll Visualizer:** Real-time graphical representation of notes and rests.
* **IR Inspector:** View the compiled JSON output of your musical score.
* **Modern Stack:** Built with React 19, Vite, and Tailwind CSS.

---

## 🚀 Getting Started

### Prerequisites

* [Node.js](https://nodejs.org/) (Latest LTS recommended)
* An API Key from [Google AI Studio](https://aistudio.google.com/) (Optional, for Gemini features)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/omniscore-ide.git](https://github.com/your-username/omniscore-ide.git)
    cd omniscore-ide
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure environment variables:**
    Create or edit the `.env.local` file in the root directory and add your API key:
    ```env
    GEMINI_API_KEY=your_actual_api_key_here
    ```

### Running the App

Start the development server:
```bash
npm run dev
