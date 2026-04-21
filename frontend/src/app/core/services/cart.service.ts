import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CartItem } from '../interfaces/cart-item';
import { ApiService } from './api.service';

export interface AddToCartPayload {
  pizzaId: number;
  size: 'small' | 'medium' | 'large';
  crust: 'classic' | 'thin' | 'cheese-burst';
  ingredientIds: number[];
}

@Injectable({
  providedIn: 'root'
})
export class CartService {
  constructor(private readonly api: ApiService) {}

  getCart(): Observable<CartItem[]> {
    return this.api.get<CartItem[]>('/cart/');
  }

  addToCart(payload: AddToCartPayload): Observable<CartItem> {
    return this.api.post<CartItem>('/cart/', payload);
  }

  updateQuantity(cartItemId: number, quantity: number): Observable<CartItem> {
    return this.api.put<CartItem>(`/cart/${cartItemId}/`, { quantity });
  }

  removeItem(cartItemId: number): Observable<{ message: string }> {
    return this.api.delete<{ message: string }>(`/cart/${cartItemId}/`);
  }

  clearCart(): Observable<{ message: string }> {
    return this.api.delete<{ message: string }>('/cart/');
  }
}
