export interface User {
  id: number;
  fullName: string;
  email: string;
  role: 'customer' | 'admin';
}
