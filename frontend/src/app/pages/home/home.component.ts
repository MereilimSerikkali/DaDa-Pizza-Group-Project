import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  isJumping = false;
  highlights = [
    {
      title: 'Build-your-own pizza',
      text: 'Select extra ingredients and see them appear directly on the pizza preview.'
    },
    {
      title: 'Fake banking checkout',
      text: 'Customers can place items in the cart and complete a safe demo payment flow.'
    },
    {
      title: 'Angular requirements covered',
      text: 'Routing, ngModel, interceptors, services, API calls, and error handling are already wired in.'
    }
  ];
  makePizzaJump(): void {
    if (this.isJumping) return;

    this.isJumping = true;

    
    setTimeout(() => {
      this.isJumping = false;
    }, 500);
  }
}
