import { Component, OnInit } from "@angular/core";
import { NgForm } from "@angular/common";
import { Router, RouteParams } from "@angular/router-deprecated";
import { HTTP_PROVIDERS } from "@angular/http";
import "rxjs/add/observable/throw";

import { AuthService } from "./auth.service";
import { User } from "./user";


@Component({
  styles: ["#login { margin-top:100px; }"],
  templateUrl: "/static/app/auth/login.component.html",
  providers: [HTTP_PROVIDERS, AuthService],
})
export class LoginComponent {

    errorMessage: string;
    submitted = false;
    user: User = new User();

    constructor(
        private router: Router,
        private routeParams: RouteParams,
        private authService: AuthService
    ) { }

    onSubmit() {
      this.authService.login(
        this.user.username, this.user.password
      ).subscribe(
        result => {
          if (result) {
            this.router.navigate(["Records"]);
          }
        },
        error => {
          this.errorMessage = error["non_field_errors"][0];
        }
      );
    }
}
