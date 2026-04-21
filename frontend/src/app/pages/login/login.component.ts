import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  mode: 'login' | 'register' = 'login';
  fullName = '';
  email = 'demo@pizzeria.com';
  password = 'pizza123';
  loading = false;
  errorMessage = '';

  readonly demoAccounts = [
    { label: 'Demo customer', email: 'demo@pizzeria.com', password: 'pizza123' },
    { label: 'Second customer', email: 'customer@pizzeria.com', password: 'customer123' },
    { label: 'Admin', email: 'admin@pizzeria.com', password: 'admin123' }
  ];

  constructor(
    private readonly authService: AuthService,
    private readonly router: Router
  ) {}

  setMode(mode: 'login' | 'register'): void {
    this.mode = mode;
    this.errorMessage = '';
  }

  fillDemo(email: string, password: string): void {
    this.mode = 'login';
    this.email = email;
    this.password = password;
    this.errorMessage = '';
  }

  submit(): void {
    this.loading = true;
    this.errorMessage = '';

    const request$ = this.mode === 'register'
      ? this.authService.register(this.fullName, this.email, this.password)
      : this.authService.login(this.email, this.password);

    request$.subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/menu']);
      },
      error: (error: Error) => {
        this.loading = false;
        this.errorMessage = error.message;
      }
    });
  }
}
