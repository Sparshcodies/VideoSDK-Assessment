# Meeting Bot with Gemini Service

## Prerequisites
Ensure you have the following installed before proceeding:
- **Python 3.11 or above**
- **Node.js**

## Project Overview
The project runs in three parts:
1. **Gemini Service** (Backend API for processing)
2. **Frontend Meeting** (Web interface for meetings)
3. **Python Assistant** (Bot that joins the meeting)

---

## Installation & Setup
### 1. Setup Gemini Service
1. Create a virtual environment:
   ```sh
   python -m venv gemini_env
   ```
2. Activate the virtual environment:
   - On Windows:
     ```sh
     gemini_env\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source gemini_env/bin/activate
     ```
3. Install dependencies:
   ```sh
   pip install -r gemini_requirements.txt
   ```
4. Run the Gemini service:
   ```sh
   uvicorn gemini_service:app --reload --port 8001
   ```
5. Once running, you can exit the virtual environment when needed by typing:
   ```sh
   deactivate
   ```

---

### 2. Setup Frontend
1. Open a new command shell.
2. Navigate to the frontend directory (if applicable) and install dependencies:
   ```sh
   npm install
   ```
3. Build the frontend:
   ```sh
   npm run build
   ```
4. Start the preview server:
   ```sh
   npm run preview
   ```
5. Join a meeting through the frontend and **note the Meeting ID**.
6. Add the Meeting ID to the `.env` file before proceeding to the next step.

---

### 3. Run Python Assistant (Meeting Bot)
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Ensure all required environment variables are set in the `.env` file.
3. Start the bot by running:
   ```sh
   python main.py
   ```

---

## Terminating the Services
To stop the project, terminate all running services by pressing **CTRL + C** in each running shell.

### Important Note
- **Python VideoSDK is not compatible with Gemini in the same environment**, so we use a separate virtual environment for the Gemini service.

Kill a process at port 

netstat -ano | findstr :8080
taskkill /PID 2660 /F

or 

npx kill-port 8080
