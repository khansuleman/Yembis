import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { CamerasComponent } from './cameras/cameras.component';
import { StartComponent } from './start/start.component';
import { MenuComponent } from './menu/menu.component';
import { CameramodalComponent } from './cameramodal/cameramodal.component';


@NgModule({
  declarations: [
    AppComponent,
    StartComponent,
    CameramodalComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
