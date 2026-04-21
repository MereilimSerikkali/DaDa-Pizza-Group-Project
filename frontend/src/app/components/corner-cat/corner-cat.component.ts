import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-corner-cat',
  templateUrl: './corner-cat.component.html',
  styleUrls: ['./corner-cat.component.css']
})
export class CornerCatComponent implements OnInit {
  showCat = false;

  constructor(private router: Router) { }

  ngOnInit(): void {
    this.checkRoute(this.router.url);

    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.checkRoute(event.urlAfterRedirects);
    });
  }

  private checkRoute(url: string): void {
    
    if (url.includes('/menu')) {
      setTimeout(() => { this.showCat = true; }, 500);
    } else {
      this.showCat = false;
    }
  }
}