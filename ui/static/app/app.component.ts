import { Component, OnInit } from "@angular/core";
import { ROUTER_DIRECTIVES, Route, Router, RouteConfig } from "@angular/router-deprecated";

import { RecordComponent } from "./record/record.component";
import { DomainComponent } from "./domain/domain.component";
import { RecordDetailComponent } from "./record/record-detail.component";
import { LoginComponent } from "./auth/login.component";
import { LogoutComponent } from "./auth/logout.component";
import { AuthService } from "./auth/auth.service";


@Component({
  selector: "dnsaas-app",
  templateUrl: "static/app/templates/app.component.html",
  directives: [ROUTER_DIRECTIVES],
  providers: [AuthService],
  styles: [" .main { margin-top:75px; }"]
})
 @RouteConfig([
  { path: "/login", name: "Login", component: LoginComponent },
  { path: "/logout", name: "Logout", component: LogoutComponent },
  { path: "/records", name: "Records", component: RecordComponent },
  { path: "/domains", name: "Domains", component: DomainComponent },
  { path: "/add-record/", name: "AddRecord", component: RecordDetailComponent },
  { path: "/record-detail/:id", name: "RecordDetail", component: RecordDetailComponent },
])
export class AppComponent implements OnInit {

  constructor(
    public router: Router,
    private authService: AuthService
  ) { }

  ngOnInit() {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(["Login"]);
    }
  }

  get isLoggedIn(): Boolean {
    return this.authService.isLoggedIn();
  }

  get username(): string {
    return this.authService.getUsername();
  }
}
