import { Ingredient } from './ingredient';

export interface CartItem {
  id: number;
  pizzaId: number;
  pizzaName: string;
  crust: 'classic' | 'thin' | 'cheese-burst';
  size: 'small' | 'medium' | 'large';
  quantity: number;
  ingredients: Ingredient[];
  imageEmoji: string;
  unitPrice: number;
}
