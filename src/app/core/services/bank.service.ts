import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BankAccount } from '../interfaces/bank-account';
import { CheckoutRequest } from '../interfaces/checkout-request';
import { ApiService } from './api.service';

export interface ChargeResponse {
  message: string;
  receiptId: string;
  remainingBalance: number;
}

@Injectable({
  providedIn: 'root'
})
export class BankService {
  constructor(private readonly api: ApiService) {}

  getAccount(): Observable<BankAccount> {
    return this.api.get<BankAccount>('/bank/account');
  }

  charge(payload: CheckoutRequest): Observable<ChargeResponse> {
    return this.api.post<ChargeResponse>('/bank/charge', payload);
  }
}
