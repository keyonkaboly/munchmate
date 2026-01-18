# MunchMate
## COSC 310 Project
#### Keyon Kaboly, Alexander Yong, Karam Hammouda, Marcus Morales

It should be noted we are using this dataset for food delivery information in our project: https://www.kaggle.com/datasets/niszarkiah/food-delivery.

## Fill out later:
Explain how to build/run the project in this ReadMe. delete everything below this before doing so (for end of project).




## Delete Below before end of project:
##### General Requirements
The project must include the following characteristics and functionalities:

Backend: Implemented using FastAPI (Python).
Basic front end implementation that should be added on the last Milestone.
API Communication: The backend should expose a RESTful API that the frontend consumes.
Testing: Use Pytest for backend testing.
Multiuser System: Must support multiple types of users interacting with the system.
Version Control & Collaboration: Git + GitHub (branches, issues, pull requests, code reviews).
Continuous Integration: GitHub Actions (automated testing on every push/pull requests).
Containerization: Use Docker for both frontend and backend.
The project must implement correct and consistent business logic that aligns with the system’s domain rules and requirements.
Software Engineering Principles: Follow the SOLID principles as we have explained them in class.
Apply general software engineering best practices (e.g., modularity, readability, maintainability, documentation) as we have explained them in class
 
##### Core Features
Feature 1: The system will allow users and restaurant owners/managers to create accounts and log in. It will handle user authentication (login), authorization (what each user is allowed to do), and basic user identity management. Different roles such as regular users and restaurant owners/managers will be supported.

Feature 2: The system will store information about restaurants and their menus. It will ensure that data is valid, properly connected (for example, menu items must belong to a restaurant), and that basic constraints are enforced, such as preventing invalid or missing values.

Feature 3: The system will allow users to browse restaurant menus and search for items or restaurants. Backend logic will handle filtering, searching, and returning paginated results.

Feature 4: The system will allow users to create and manage food orders. It will ensure that orders are consistent, correctly stored, and follow business logic for the domain (for example, an order cannot be modified after it is completed).

Feature 5: The system will manage delivery-related information. It will support assigning deliveries and tracking basic delivery status as part of the backend logic.

Feature 6: The system will calculate the total cost of an order, including item prices, delivery fees, and taxes. These calculations will follow predefined business rules implemented in the backend.
Feature 7 (simulated): The system will simulate payment processing. No real payment gateway will be used, but the system will follow the correct workflow for accepting or rejecting a payment and updating the order status.

Feature 8: The system will generate notifications or events when important actions occur, such as order creation or status changes.

Feature 9 (Optional): The system may allow users to rate and review completed orders or restaurants. This feature is optional and can be implemented if time permits.

Feature 10 (Optional): The system may include administrative features such as viewing all orders and generating simple reports or statistics (for example, average delivery time or most popular restaurants). This feature is optional.
 

##### Quality Features
The system should be designed to be reliable, secure, and maintainable. It should provide acceptable performance for typical usage scenarios and handle data consistently and safely. The backend APIs should be easy to understand, well-structured, and follow standard design practices.
The system should protect user data through proper authentication and authorization mechanisms and prevent invalid or inconsistent system states. It should be robust enough to handle incorrect input and unexpected situations without failure.
The codebase should be modular and well-organized to support future extensions and testing. 

The Frontend should:
The front end should be simple and implemented in M4
It must provide clear pathways for users to find, search, and interact with the resources or items they need
Admins should have a dedicated interface that allows them to efficiently manage data, monitor activity, and apply administrative actions (e.g., penalties, edits, or deletions)
