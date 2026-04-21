import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { AuthResponse } from '../interfaces/auth-response';
import { User } from '../interfaces/user';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly tokenKey = 'dada_token';
  private readonly userKey = 'pizza_user';
  private readonly userSubject = new BehaviorSubject<User | null>(this.readStoredUser());

  readonly currentUser$ = this.userSubject.asObservable();

  constructor(private readonly api: ApiService) {}

  login(email: string, password: string): Observable<AuthResponse> {
    return this.api.post<AuthResponse>('/auth/login/', { email, password }).pipe(
      tap((response) => this.storeSession(response))
    );
  }

  register(fullName: string, email: string, password: string): Observable<AuthResponse> {
    return this.api.post<AuthResponse>('/auth/register/', { fullName, email, password }).pipe(
      tap((response) => this.storeSession(response))
    );
  }

  logout(): Observable<{ message: string }> {
    return this.api.post<{ message: string }>('/auth/logout/', {}).pipe(
      tap(() => this.clearSession())
    );
  }

  forceLogout(): void {
    this.clearSession();
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  private readStoredUser(): User | null {
    const raw = localStorage.getItem(this.userKey);
    return raw ? (JSON.parse(raw) as User) : null;
  }

  private storeSession(response: AuthResponse): void {
    localStorage.setItem(this.tokenKey, response.token);
    localStorage.setItem(this.userKey, JSON.stringify(response.user));
    this.userSubject.next(response.user);
  }

  private clearSession(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    this.userSubject.next(null);
  }
}
