import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  get<T>(endpoint: string): Observable<T> {
    return this.handle(this.http.get<T>(`${this.baseUrl}${endpoint}`));
  }

  post<T>(endpoint: string, body: unknown): Observable<T> {
    return this.handle(this.http.post<T>(`${this.baseUrl}${endpoint}`, body));
  }

  put<T>(endpoint: string, body: unknown): Observable<T> {
    return this.handle(this.http.put<T>(`${this.baseUrl}${endpoint}`, body));
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.handle(this.http.delete<T>(`${this.baseUrl}${endpoint}`));
  }

  private handle<T>(request$: Observable<T>): Observable<T> {
    return request$.pipe(
      catchError((error: HttpErrorResponse) => {
        const message = error.error?.message || 'The server could not process the request.';
        return throwError(() => new Error(message));
      })
    );
  }
}
