export interface CheckoutRequest {
  fullName: string;
  email: string;
  address: string;
  cardNumber: string;
  expiry: string;
  cvv: string;
  amount: number;
}
