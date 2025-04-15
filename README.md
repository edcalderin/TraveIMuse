# TravelMuse: AI-Powered Itinerary Generator

## Overview

TravelMuse is an intelligent travel planning application that leverages Generative AI to create personalized travel itineraries and visualize them on an interactive map.

Key Features

* AI-Powered Itinerary Creation: Using OpenAI's language models and advanced prompt engineering techniques, TravelMuse generates tailored travel plans based on your preferences, budget, and timeframe.
* Interactive Map Visualization: Each point in your itinerary is automatically plotted on an interactive map, allowing you to visualize your journey and understand the geographical flow of your trip.
* Customizable Experience: Fine-tune your itinerary with simple natural language requests like "add more outdoor activities" or "reduce walking distance between locations."
* User-Friendly Interface: Built with Gradio, the application offers an intuitive, responsive interface accessible from any device with a web browser.
* LangChain Integration: Utilizes LangChain to enhance the AI's context awareness and maintain coherent travel recommendations that account for logical routing and time constraints.

The application combines the creative power of AI with practical mapping tools to take the stress out of travel planning while ensuring you discover the perfect mix of popular attractions and hidden gems.

## Prerequisites
- Python 3.12 or higher
- Poetry

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/edcalderin/TraveIMuse.git
cd TraveIMuse
```

### 2. Create and activate the Poetry environment
```bash
# Create the env directory within the project
poetry config virtualenvs.create false --local

# Create a new Poetry environment
poetry install --no-root

# Activate the environment
poetry env activate
```

### 3. Verify the installation
```bash
# Verify that the environment is active
poetry env info

# The activated environment should appear first.
```

## Usage

### Development workflow
1. Rename `.env.example` to `.env` and set the variables with your own api key values.
    ```
    OPENAI_API_KEY=
    GOOGLE_MAPS_API_KEY=
    ```

3. Run Gradio app:
    ```bash
    python -m gradio_app
    ```

3. Write your itinerary and enjoy the app!

### Lint
Style the code with Ruff:

```bash
ruff format .
ruff check . --fix
```
### Removing the environment
When you're done working on the project, remove the Poetry environment:

```bash
poetry env remove
```

## Contact
**LinkedIn:** https://www.linkedin.com/in/erick-calderin-5bb6963b/  
**e-mail:** edcm.erick@gmail.com