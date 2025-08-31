# This project is a demo application for source.dev


 The project uses FastAPI on the backend to serve log files efficiently and Vue.js on the frontend to browse through the logs and perform searches


## Getting Started
### Prerequisites

Python 3.10+
Node.js 16+ (with npm)

### Installation
1. Clone the repository:
   Navigate to a directory of your choice and clone the repository by using pasting the following command in the terminal

    git clone https://github.com/arjunjoshua/sourcedev_logs.git (https)
    
2. Navigate to the project directory:

    cd sourcedev_logs

3. Set up a virtual environment (optional but recommended):

    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

4. Install the required Python packages:

    pip install -r requirements.txt

5. Navigate to the frontend directory and install the dependencies:
    
    cd ..
    cd frontend
    npm install

6. You will also need to download the log files which are too large to be included in the repository.
    You can download them from this link: https://drive.google.com/file/d/1MRjzmMy5vVzuGYSb-_lxuCDKsh3sKLCe/view?usp=drive_link

    Extract the contents to the backend/build_log_examples directory and you are good to go :)

### Running the Application
1. Start the FastAPI backend server:

    cd ..
    cd backend
    ./main.py (the server is configured to run using uvicorn)#
2. The backend server will start at http://localhost:5000

3. In a new terminal, navigate to the frontend directory and start the Vue.js development server:

    cd ..
    cd frontend
    npm run dev

4. The frontend server will start at http://localhost:5173

5. Open your web browser and go to http://localhost:5173 to access the application.


### Note to the source.dev team: 
I have built a monolith in App.vue on the frontend to make things simpler in development.
I did not want to unnecessarily implement a state management library or pass props down for the demo.