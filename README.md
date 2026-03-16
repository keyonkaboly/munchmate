# MunchMate
## COSC 310 Project
#### Keyon Kaboly, Alexander Yong, Karam Hammouda, Marcus Morales

It should be noted we are using this dataset for food delivery information in our project: https://www.kaggle.com/datasets/niszarkiah/food-delivery.

#### Docker Commands
Ensure proper directory: cd .../munchmate
Then run following below commands Keep in mind that you should navigate to localhost:8000/docs (can change that in browser URL):
- docker context use default
- docker compose up --build --no-deps -d backend
- docker compose ps
- curl http://localhost:8000/
