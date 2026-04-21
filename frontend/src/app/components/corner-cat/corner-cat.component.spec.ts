import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CornerCatComponent } from './corner-cat.component';

describe('CornerCatComponent', () => {
  let component: CornerCatComponent;
  let fixture: ComponentFixture<CornerCatComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CornerCatComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CornerCatComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
