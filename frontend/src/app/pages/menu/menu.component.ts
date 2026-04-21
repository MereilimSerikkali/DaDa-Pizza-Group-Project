import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Ingredient } from '../../core/interfaces/ingredient';
import { Pizza } from '../../core/interfaces/pizza';
import { CartService } from '../../core/services/cart.service';
import { PizzaService } from '../../core/services/pizza.service';

interface PreviewDot {
  key: string;
  icon: string;
  cssClass: string;
  top: string;
  left: string;
}

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent {
  pizzas: Pizza[] = [];
  ingredients: Ingredient[] = [];
  selectedPizza: Pizza | null = null;
  selectedIngredientIds: number[] = [];
  previewDots: PreviewDot[] = [];
  size: 'small' | 'medium' | 'large' = 'medium';
  crust: 'classic' | 'thin' | 'cheese-burst' = 'classic';
  loading = false;
  errorMessage = '';
  successMessage = '';

  private readonly toppingPositions: Record<number, Array<{ top: string; left: string }>> = {
    1: [
      { top: '18%', left: '23%' },
      { top: '31%', left: '58%' },
      { top: '55%', left: '26%' },
      { top: '62%', left: '58%' }
    ],
    2: [
      { top: '22%', left: '45%' },
      { top: '38%', left: '22%' },
      { top: '55%', left: '47%' },
      { top: '70%', left: '37%' }
    ],
    3: [
      { top: '28%', left: '68%' },
      { top: '48%', left: '64%' },
      { top: '63%', left: '19%' },
      { top: '45%', left: '36%' }
    ],
    4: [
      { top: '18%', left: '52%' },
      { top: '34%', left: '34%' },
      { top: '58%', left: '68%' },
      { top: '72%', left: '54%' }
    ],
    5: [
      { top: '27%', left: '28%' },
      { top: '42%', left: '52%' },
      { top: '62%', left: '34%' },
      { top: '50%', left: '74%' }
    ],
    6: [
      { top: '24%', left: '62%' },
      { top: '40%', left: '18%' },
      { top: '58%', left: '48%' },
      { top: '70%', left: '63%' }
    ],
    7: [
      { top: '20%', left: '35%' },
      { top: '32%', left: '73%' },
      { top: '57%', left: '58%' },
      { top: '66%', left: '28%' }
    ],
    8: [
      { top: '25%', left: '17%' },
      { top: '37%', left: '44%' },
      { top: '53%', left: '71%' },
      { top: '67%', left: '46%' }
    ]
  };

  constructor(
    private readonly pizzaService: PizzaService,
    private readonly cartService: CartService,
    private readonly router: Router
  ) {}

  loadMenu(): void {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    forkJoin({
      pizzas: this.pizzaService.getPizzas(),
      ingredients: this.pizzaService.getIngredients()
    }).subscribe({
      next: ({ pizzas, ingredients }) => {
        this.pizzas = pizzas;
        this.ingredients = ingredients;
        this.loading = false;

        if (!this.selectedPizza && pizzas.length > 0) {
          this.openCustomizer(pizzas[0]);
        }
      },
      error: (error: Error) => {
        this.loading = false;
        this.errorMessage = error.message;
      }
    });
  }

  openCustomizer(pizza: Pizza): void {
    this.selectedPizza = pizza;
    this.selectedIngredientIds = [...pizza.defaultIngredientIds];
    this.size = 'medium';
    this.crust = 'classic';
    this.successMessage = '';
    this.refreshPreview();
  }

  isSelected(ingredientId: number): boolean {
    return this.selectedIngredientIds.includes(ingredientId);
  }

  toggleIngredient(ingredientId: number): void {
    if (this.isSelected(ingredientId)) {
      this.selectedIngredientIds = this.selectedIngredientIds.filter((id) => id !== ingredientId);
    } else {
      this.selectedIngredientIds = [...this.selectedIngredientIds, ingredientId];
    }
    this.refreshPreview();
  }

  updatePizzaVariant(): void {
    this.refreshPreview();
  }

  addCurrentPizzaToCart(): void {
    if (!this.selectedPizza) {
      return;
    }

    this.errorMessage = '';
    this.successMessage = '';

    this.cartService
      .addToCart({
        pizzaId: this.selectedPizza.id,
        ingredientIds: this.selectedIngredientIds,
        size: this.size,
        crust: this.crust
      })
      .subscribe({
        next: () => {
          this.successMessage = `${this.selectedPizza?.name} added to the cart.`;
        },
        error: (error: Error) => {
          this.errorMessage = error.message;
          if (error.message.includes('log in')) {
            this.router.navigate(['/login']);
          }
        }
      });
  }

  getIngredientName(ingredientId: number): string {
    return this.ingredients.find((item) => item.id === ingredientId)?.name ?? 'Ingredient';
  }

  private refreshPreview(): void {
    this.previewDots = this.selectedIngredientIds.flatMap((ingredientId) => {
      const ingredient = this.ingredients.find((item) => item.id === ingredientId);
      const positions = this.toppingPositions[ingredientId] ?? [];

      if (!ingredient) {
        return [];
      }

      return positions.map((position, index) => ({
        key: `${ingredientId}-${index}`,
        icon: ingredient.icon,
        cssClass: ingredient.cssClass,
        top: position.top,
        left: position.left
      }));
    });
  }
}
