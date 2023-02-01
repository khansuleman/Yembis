import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CameramodalComponent } from './cameramodal.component';

describe('CameramodalComponent', () => {
  let component: CameramodalComponent;
  let fixture: ComponentFixture<CameramodalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CameramodalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CameramodalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
