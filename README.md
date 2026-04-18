# Burgundy Pizzeria Front End (Angular)

This project is a front-end Angular demo for a pizzeria with a burgundy-and-white design system.
It includes:

- Routing with 4 named routes: `/home`, `/login`, `/menu`, `/cart`
- JWT login and logout flow
- HTTP interceptor that adds `Authorization: Bearer <token>`
- Fake backend interceptor so the app works without a real server
- API services and TypeScript interfaces
- Dynamic pizza customizer with ingredient preview on top of the pizza
- Cart page with quantity updates, removal, refresh, and fake payment
- Template-driven forms with `[(ngModel)]`
- Conditional rendering and looping with Angular `@if` and `@for`
- Graceful error messages for failed API requests

## Demo credentials

- Email: `demo@pizzeria.com`
- Password: `pizza123`

## How to run

```bash
npm install
npm start
```

Then open the local Angular development URL shown in the terminal.

## Main API requests triggered by clicks

1. **Login** → `POST /auth/login`
2. **Load today's pizzas** → `GET /pizzas` and `GET /ingredients`
3. **Add customized pizza to cart** → `POST /cart`
4. **Refresh cart & bank** → `GET /cart` and `GET /bank/account`
5. **+ / - quantity** → `PUT /cart/:id`
6. **Remove item** → `DELETE /cart/:id`
7. **Pay now** → `POST /bank/charge`, then `DELETE /cart`
8. **Logout** → `POST /auth/logout`

## Notes

- The payment system is intentionally fake and safe for demo/coursework use.
- The fake backend stores cart and bank data in `localStorage`.
- The cart route is protected by an auth guard.
