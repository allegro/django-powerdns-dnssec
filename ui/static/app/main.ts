import { enableProdMode, provide } from "@angular/core";
import { bootstrap } from "@angular/platform-browser-dynamic";
import { HTTP_PROVIDERS } from "@angular/http";
import { ROUTER_PROVIDERS } from "@angular/router-deprecated";
import { Location, LocationStrategy, HashLocationStrategy } from "@angular/common";

import { AppComponent } from "./app.component";
import { AuthService } from "./auth/auth.service";
import { ConfigService } from "./config.service";
import { HttpClient } from "./http-client";
import { LocalStorage } from "./local-storage";

// get java script debug variable from ui/templates/ui/index.html
declare var debug: any;

if (!debug) {
  enableProdMode();
}

bootstrap(AppComponent, [
  ROUTER_PROVIDERS,
  HTTP_PROVIDERS,
  provide(LocationStrategy, {useClass: HashLocationStrategy}),
  provide(LocalStorage, {useClass: LocalStorage}),
  provide(AuthService, {useClass: AuthService}),
  provide(HttpClient, {useClass: HttpClient}),
  provide(ConfigService, {useClass: ConfigService}),
]);
