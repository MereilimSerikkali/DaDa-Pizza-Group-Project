import { Component, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';
import { BankAccount } from '../../core/interfaces/bank-account';
import { CartItem } from '../../core/interfaces/cart-item';
import { BankService } from '../../core/services/bank.service';
import { CartService } from '../../core/services/cart.service';

@Component({
  selector: 'app-cart',
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent implements OnInit {
  cartItems: CartItem[] = [];
  account: BankAccount | null = null;
  loading = false;
  paying = false;
  errorMessage = '';
  successMessage = '';

  paymentForm = {
    fullName: 'Lina Rossi',
    email: 'demo@pizzeria.com',
    address: '17 Burgundy Street',
    cardNumber: '4242424242424242',
    expiry: '12/28',
    cvv: '123'
  };

  constructor(
    private readonly cartService: CartService,
    private readonly bankService: BankService
  ) {}

  ngOnInit(): void {
    this.refreshData();
  }

  refreshData(): void {
    this.loading = true;
    this.errorMessage = '';

    forkJoin({
      cart: this.cartService.getCart(),
      account: this.bankService.getAccount()
    }).subscribe({
      next: ({ cart, account }) => {
        this.cartItems = cart;
        this.account = account;
        this.loading = false;
      },
      error: (error: Error) => {
        this.loading = false;
        this.errorMessage = error.message;
      }
    });
  }

  increase(item: CartItem): void {
    this.updateQuantity(item, item.quantity + 1);
  }

  decrease(item: CartItem): void {
    if (item.quantity === 1) {
      this.remove(item);
      return;
    }
    this.updateQuantity(item, item.quantity - 1);
  }

  remove(item: CartItem): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.cartService.removeItem(item.id).subscribe({
      next: (response) => {
        this.successMessage = response.message;
        this.refreshData();
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
      }
    });
  }

  payNow(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (this.cartTotal <= 0) {
      this.errorMessage = 'Your cart is empty.';
      return;
    }

    this.paying = true;

    this.bankService
      .charge({
        ...this.paymentForm,
        amount: this.cartTotal
      })
      .subscribe({
        next: (response) => {
          this.cartService.clearCart().subscribe({
            next: () => {
              this.paying = false;
              this.successMessage = `${response.message} Receipt: ${response.receiptId}. Remaining balance: $${response.remainingBalance.toFixed(2)}.`;
              this.refreshData();
            },
            error: (clearError: Error) => {
              this.paying = false;
              this.errorMessage = clearError.message;
              this.refreshData();
            }
          });
        },
        error: (error: Error) => {
          this.paying = false;
          this.errorMessage = error.message;
        }
      });
  }

  get cartTotal(): number {
    return this.cartItems.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0);
  }

  private updateQuantity(item: CartItem, quantity: number): void {
    this.errorMessage = '';
    this.successMessage = '';

    this.cartService.updateQuantity(item.id, quantity).subscribe({
      next: () => {
        this.successMessage = 'Cart updated.';
        this.refreshData();
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
      }
    });
  }
}
