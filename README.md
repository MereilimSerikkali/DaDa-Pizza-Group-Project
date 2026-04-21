# DaDa Pizza - Web Development 2026
Present By: Alpysbay Tomiris, Serikkali Mereilim, Kudaibergen Aisha

DaDa Pizza is a full-stack web application for an online pizza ordering system. The project was developed using Angular for the front end and Django with Django REST Framework for the back end. The application allows users to register, log in, browse pizzas, add items to a cart, place orders, and manage their session securely. It also includes an admin panel in Django for managing pizzas, categories, ingredients, and customer orders.

On the front end, Angular was used to build a responsive single-page application with routing, reusable components, form handling, API integration, and authentication support. Services and interfaces were created to communicate with the back-end API, while HTTP interceptors were used to attach authentication tokens to protected requests. The interface includes multiple pages such as login/register, menu, cart, and home, with CSS styling for a user-friendly experience.

On the back end, Django and Django REST Framework were used to build a RESTful API. The system includes models such as pizzas, ingredients, categories, orders, and cart items, with serializers, function-based views, and class-based views to support CRUD operations and business logic. JWT authentication was implemented for secure login, logout, and token refresh. CORS was configured so the Angular front end could communicate with the Django server during development.

For API testing and demonstration, Postman was used. A Postman collection was prepared with requests for registration, login, token refresh, logout, pizza retrieval, cart operations, payment simulation, and order creation. This makes it easier to test all endpoints and demonstrate that the API works correctly.

In summary, DaDa Pizza is a complete Angular + Django + DRF + JWT + Postman project that demonstrates both front-end and back-end development, user authentication, API integration, and full-stack application design.
