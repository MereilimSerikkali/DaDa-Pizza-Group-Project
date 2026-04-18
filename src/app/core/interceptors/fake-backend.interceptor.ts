import { Injectable } from '@angular/core';
import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpResponse
} from '@angular/common/http';
import { Observable, delay, of, throwError } from 'rxjs';
import { Ingredient } from '../interfaces/ingredient';
import { Pizza } from '../interfaces/pizza';
import { CartItem } from '../interfaces/cart-item';
import { BankAccount } from '../interfaces/bank-account';

interface DemoUser {
  id: number;
  fullName: string;
  email: string;
  password: string;
  role: 'customer' | 'admin';
}

@Injectable()
export class FakeBackendInterceptor implements HttpInterceptor {
  private readonly users: DemoUser[] = [
    {
      id: 1,
      fullName: 'Lina Rossi',
      email: 'demo@pizzeria.com',
      password: 'pizza123',
      role: 'customer'
    }
  ];

  private readonly ingredients: Ingredient[] = [
    { id: 1, name: 'Pepperoni', price: 1.5, icon: '●', cssClass: 'pepperoni' },
    { id: 2, name: 'Mushrooms', price: 1.1, icon: '◔', cssClass: 'mushroom' },
    { id: 3, name: 'Olives', price: 0.9, icon: '◉', cssClass: 'olive' },
    { id: 4, name: 'Basil', price: 0.8, icon: '✦', cssClass: 'basil' },
    { id: 5, name: 'Mozzarella', price: 1.3, icon: '✹', cssClass: 'mozzarella' },
    { id: 6, name: 'Chicken', price: 1.7, icon: '◆', cssClass: 'chicken' },
    { id: 7, name: 'Jalapeños', price: 1.0, icon: '✦', cssClass: 'jalapeno' },
    { id: 8, name: 'Cherry Tomatoes', price: 1.0, icon: '●', cssClass: 'tomato' }
  ];

  private readonly pizzas: Pizza[] = [
    {
      id: 1,
      name: 'Royal Margherita',
      description: 'Fresh basil, silky mozzarella, and a rich tomato sauce base.',
      imageEmoji: '🍕',
      price: 8.9,
      defaultIngredientIds: [4, 5, 8]
    },
    {
      id: 2,
      name: 'Burgundy Pepperoni',
      description: 'A bold favorite with pepperoni, mozzarella, and olives.',
      imageEmoji: '🍕',
      price: 10.5,
      defaultIngredientIds: [1, 3, 5]
    },
    {
      id: 3,
      name: 'Forest Chicken',
      description: 'Roasted chicken, mushrooms, mozzarella, and herbs.',
      imageEmoji: '🍕',
      price: 11.3,
      defaultIngredientIds: [2, 4, 5, 6]
    }
  ];

  private readonly cartKey = 'pizza_demo_cart';
  private readonly bankKey = 'pizza_demo_bank';

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    if (!req.url.includes('/api/')) {
      return next.handle(req);
    }

    try {
      return this.handleRequest(req);
    } catch (error) {
      const httpError = error instanceof HttpErrorResponse
        ? error
        : new HttpErrorResponse({ status: 500, error: { message: 'Unexpected fake backend error.' } });
      return throwError(() => httpError);
    }
  }

  private handleRequest(req: HttpRequest<unknown>): Observable<HttpEvent<unknown>> {
    const { url, method, body, headers } = req;

    if (url.endsWith('/auth/login') && method === 'POST') {
      return this.ok(this.login(body as { email: string; password: string }));
    }

    if (url.endsWith('/auth/logout') && method === 'POST') {
      return this.ok({ message: 'Logged out successfully.' });
    }

    if (url.endsWith('/pizzas') && method === 'GET') {
      return this.ok(this.pizzas);
    }

    if (url.endsWith('/ingredients') && method === 'GET') {
      return this.ok(this.ingredients);
    }

    if (url.endsWith('/cart') && method === 'GET') {
      this.ensureAuthorized(headers.get('Authorization'));
      return this.ok(this.readCart());
    }

    if (url.endsWith('/cart') && method === 'POST') {
      this.ensureAuthorized(headers.get('Authorization'));
      return this.ok(this.addToCart(body as { pizzaId: number; ingredientIds: number[]; size: string; crust: string }));
    }

    if (url.match(/\/cart\/\d+$/) && method === 'PUT') {
      this.ensureAuthorized(headers.get('Authorization'));
      const cartId = Number(url.split('/').pop());
      return this.ok(this.updateCartItem(cartId, body as { quantity: number }));
    }

    if (url.match(/\/cart\/\d+$/) && method === 'DELETE') {
      this.ensureAuthorized(headers.get('Authorization'));
      const cartId = Number(url.split('/').pop());
      return this.ok(this.removeCartItem(cartId));
    }

    if (url.endsWith('/cart') && method === 'DELETE') {
      this.ensureAuthorized(headers.get('Authorization'));
      localStorage.setItem(this.cartKey, JSON.stringify([]));
      return this.ok({ message: 'Cart cleared.' });
    }

    if (url.endsWith('/bank/account') && method === 'GET') {
      this.ensureAuthorized(headers.get('Authorization'));
      return this.ok(this.readBank());
    }

    if (url.endsWith('/bank/charge') && method === 'POST') {
      this.ensureAuthorized(headers.get('Authorization'));
      return this.ok(this.charge(body as { amount: number; cardNumber: string; cvv: string; expiry: string }));
    }

    return throwError(() => new HttpErrorResponse({ status: 404, error: { message: 'Endpoint not found.' } }));
  }

  private login(payload: { email: string; password: string }) {
    const user = this.users.find(
      (candidate) => candidate.email === payload.email && candidate.password === payload.password
    );

    if (!user) {
      throw new HttpErrorResponse({
        status: 401,
        error: { message: 'Invalid credentials. Try demo@pizzeria.com / pizza123.' }
      });
    }

    this.ensureSeededBank();

    return {
      token: 'demo-jwt-token',
      user: {
        id: user.id,
        fullName: user.fullName,
        email: user.email,
        role: user.role
      }
    };
  }

  private addToCart(payload: { pizzaId: number; ingredientIds: number[]; size: string; crust: string }): CartItem {
    const pizza = this.pizzas.find((item) => item.id === payload.pizzaId);

    if (!pizza) {
      throw new HttpErrorResponse({ status: 404, error: { message: 'Pizza not found.' } });
    }

    const selectedIngredients = this.ingredients.filter((ingredient) => payload.ingredientIds.includes(ingredient.id));
    const sizeMultiplier = payload.size === 'small' ? 0.9 : payload.size === 'large' ? 1.35 : 1;
    const crustPrice = payload.crust === 'cheese-burst' ? 2.2 : payload.crust === 'thin' ? 0.5 : 0;
    const ingredientsPrice = selectedIngredients.reduce((sum, item) => sum + item.price, 0);
    const unitPrice = Number(((pizza.price + ingredientsPrice + crustPrice) * sizeMultiplier).toFixed(2));

    const cart = this.readCart();
    const newItem: CartItem = {
      id: Date.now(),
      pizzaId: pizza.id,
      pizzaName: pizza.name,
      crust: payload.crust as CartItem['crust'],
      size: payload.size as CartItem['size'],
      quantity: 1,
      ingredients: selectedIngredients,
      imageEmoji: pizza.imageEmoji,
      unitPrice
    };

    cart.push(newItem);
    localStorage.setItem(this.cartKey, JSON.stringify(cart));
    return newItem;
  }

  private updateCartItem(cartId: number, payload: { quantity: number }): CartItem {
    const cart = this.readCart();
    const item = cart.find((entry) => entry.id === cartId);

    if (!item) {
      throw new HttpErrorResponse({ status: 404, error: { message: 'Cart item not found.' } });
    }

    item.quantity = Math.max(1, Math.min(10, payload.quantity));
    localStorage.setItem(this.cartKey, JSON.stringify(cart));
    return item;
  }

  private removeCartItem(cartId: number): { message: string } {
    const cart = this.readCart().filter((entry) => entry.id !== cartId);
    localStorage.setItem(this.cartKey, JSON.stringify(cart));
    return { message: 'Item removed from cart.' };
  }

  private charge(payload: { amount: number; cardNumber: string; cvv: string; expiry: string }) {
    const normalizedNumber = payload.cardNumber.replace(/\s+/g, '');

    if (!/^\d{16}$/.test(normalizedNumber)) {
      throw new HttpErrorResponse({ status: 400, error: { message: 'Card number must contain 16 digits.' } });
    }

    if (!/^\d{3}$/.test(payload.cvv)) {
      throw new HttpErrorResponse({ status: 400, error: { message: 'CVV must contain 3 digits.' } });
    }

    if (!/^\d{2}\/\d{2}$/.test(payload.expiry)) {
      throw new HttpErrorResponse({ status: 400, error: { message: 'Expiry must be in MM/YY format.' } });
    }

    const bank = this.readBank();

    if (payload.amount <= 0) {
      throw new HttpErrorResponse({ status: 400, error: { message: 'Cart total must be greater than zero.' } });
    }

    if (bank.balance < payload.amount) {
      throw new HttpErrorResponse({ status: 402, error: { message: 'Insufficient demo balance. Refresh or reduce the cart.' } });
    }

    bank.balance = Number((bank.balance - payload.amount).toFixed(2));
    localStorage.setItem(this.bankKey, JSON.stringify(bank));

    return {
      message: 'Demo payment approved. Your pizza is being prepared.',
      receiptId: `R-${Math.floor(Math.random() * 900000 + 100000)}`,
      remainingBalance: bank.balance
    };
  }

  private ensureAuthorized(header: string | null): void {
    if (!header || header !== 'Bearer demo-jwt-token') {
      throw new HttpErrorResponse({ status: 401, error: { message: 'Please log in to continue.' } });
    }
  }

  private readCart(): CartItem[] {
    const stored = localStorage.getItem(this.cartKey);
    return stored ? (JSON.parse(stored) as CartItem[]) : [];
  }

  private ensureSeededBank(): void {
    if (!localStorage.getItem(this.bankKey)) {
      const bank: BankAccount = {
        holder: 'Lina Rossi',
        balance: 150,
        currency: 'USD',
        last4: '4242'
      };
      localStorage.setItem(this.bankKey, JSON.stringify(bank));
    }
  }

  private readBank(): BankAccount {
    this.ensureSeededBank();
    return JSON.parse(localStorage.getItem(this.bankKey) as string) as BankAccount;
  }

  private ok(body: unknown): Observable<HttpEvent<unknown>> {
    return of(new HttpResponse({ status: 200, body })).pipe(delay(500));
  }
}
