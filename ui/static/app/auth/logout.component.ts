import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router-deprecated";
import { AuthService } from "./auth.service";


@Component({
  template: "",
  providers: [AuthService],
})
export class LogoutComponent implements OnInit {

    constructor(
      private router: Router,
      private authService: AuthService
    ) { }

    ngOnInit() {
      this.authService.logout();
      this.router.navigate(["Login"]);
    }
}
