import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Ingredient } from '../interfaces/ingredient';
import { Pizza } from '../interfaces/pizza';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class PizzaService {
  constructor(private readonly api: ApiService) {}

  getPizzas(): Observable<Pizza[]> {
    return this.api.get<Pizza[]>('/pizzas/');
  }

  getIngredients(): Observable<Ingredient[]> {
    return this.api.get<Ingredient[]>('/ingredients/');
  }
}
