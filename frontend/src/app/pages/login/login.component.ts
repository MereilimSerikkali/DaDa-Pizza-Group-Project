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

  email = 'demo@pizzeria.com';
  password = 'pizza123';
  fullName = '';
  loading = false;
  errorMessage = '';

  readonly demoAccounts = [
    { email: 'demo@pizzeria.com', password: 'pizza123', label: 'Demo customer' },
    { email: 'customer@pizzeria.com', password: 'customer123', label: 'Second customer' },
    { email: 'admin@pizzeria.com', password: 'admin123', label: 'Admin account' }
  ];

  constructor(
    private readonly authService: AuthService,
    private readonly router: Router
  ) {}

  setMode(mode: 'login' | 'register'): void {
    this.mode = mode;
    this.errorMessage = '';
  }

  useDemoAccount(email: string, password: string): void {
    this.mode = 'login';
    this.email = email;
    this.password = password;
    this.errorMessage = '';
  }

  submit(): void {
    this.loading = true;
    this.errorMessage = '';

    const request$ = this.mode === 'login'
      ? this.authService.login(this.email, this.password)
      : this.authService.register(this.fullName, this.email, this.password);

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
