Project Title:-
-SignalFire

Project Description:-
-Signalfire is an AI-powered Career Intelligence Platform that helps students and professionals discover personalized jobs, internships, hackathons, scholarships, and learning opportunities.
-The platform analyzes a user's profile, resume, skills, and interests using AI to recommend the best opportunities from multiple sources.

Features:-

- AI Resume Analysis
- Personalized Recommendations
- Job Search
- Internship Search
- Hackathon Discovery
- Scholarship Finder
- Learning Roadmaps
- User Authentication
- Resume Upload
- Dashboard Analytics
- Saved Opportunities
- AI Career Assistant

 Tech Stack:-

Frontend
- React
- TypeScript
- Tailwind CSS
- Vite

Backend
- FastAPI
- Python

Database
- PostgreSQL

Authentication
- JWT

AI
- Gemini API
- Tavily Search API
- JSearch API

Deployment
- Cloudflare Pages
- Render

Note:- 
-We had developed Two UI and with Some feautre modification too.

1) Black and Minimal Features.

2) White and Blue Advanced Features.

Frontend And Backend Activation:-

Steps To Run Our Project:-
tep 1: Open VS Code

Open the Siganlfire folder By cloning or online Activation.

Example:

Signalfire/
│
├── black_theme/|──frontend
               |──backend  

├── white_theme/|──frontend
                |──backend
                
Step 2: Open Two Terminals

In VS Code:

Terminal → New Terminal

Create 2 terminals.

You should have:

Terminal 1
Terminal 2

Step 3: Run the Backend

In Terminal 1:-

Move to the backend folder.
cd backend
If using Windows and a virtual environment:

venv\Scripts\activate
or
.\venv\Scripts\activate

You'll see something like
(venv)
Now install packages if needed:
pip install -r requirements.txt
Run FastAPI:

uvicorn app.main:app --reload
If your main file is named differently:
uvicorn main:app --reload
You should see something like:
INFO: Uvicorn running on
http://127.0.0.1:8000

Step 4: Test the Backend:-

Open your browser:

http://127.0.0.1:8000
or
http://127.0.0.1:8000/docs

Swagger UI should open.
If it does, the backend is running successfully.

Step 5: Run the Frontend:-

In Terminal 2:-

Go to the frontend folder.
cd frontend
Install packages:
npm install

Run:

npm run dev
or
npm start
depending on your project.

You should see something like:

Local:

http://localhost:517
or
http://localhost:3000

Step 6: Open the Frontend:-

Open
http://localhost:5173
or
http://localhost:3000
The frontend should load.

Step 7: Connect Frontend to Backend

If your frontend needs to call the backend, make sure the API URL is set correctly.
For local development, it is usually:

http://localhost:8000

Example with Axios:

axios.get("http://localhost:8000/api/jobs")
or
fetch("http://localhost:8000/api/jobs")

Step 8: Both Servers Should Be Running
Your terminals should look like this:
Terminal 1 (Backend)
Terminal 2 (Frontend)


Future Improvements

- Mobile App
- AI Interview Preparation
- ATS Resume Score
- AI Career Coach
- Company Matching
- Salary Prediction
- Skill Gap Analysis

Team - Phoenix protocol
- Sakthivishal.T 714024243173
- Mohamed irfan.M 714024243122
- Premraj.R 714024243153

ThankYou!
