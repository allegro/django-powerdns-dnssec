import { Injectable, Inject } from "@angular/core";
import { Http, Headers, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { LocalStorage } from "../local-storage";
import "rxjs/add/operator/map";


@Injectable()
export class AuthService {

  public loggedIn: boolean = false;

  constructor(
    private http: Http,
    private localStorage: LocalStorage
  ) { }

  login(username: string, password: string) {
    let headers = new Headers();
    headers.append("Content-Type", "application/json");

    return this.http
      .post(
      "/api-token-auth/",
      JSON.stringify({"username": username, "password": password }),
        { headers }
      )
      .map(res => res.json())
      .map((res) => {
        if (res.token) {
          this.localStorage.set("auth_token", res.token);
          this.localStorage.set("auth_username", username);
          this.localStorage.set("auth_user_id", res.user_id);
          this.localStorage.set("auth_user_fullname", res.user);
          return true;
        }
        return false;
      });
  }

  getToken(): string {
    return this.localStorage.get("auth_token");
  }

  isLoggedIn(): boolean {
    return (this.localStorage.get("auth_token")) ? true : false;
  }

  logout() {
    this.localStorage.remove("auth_token");
    this.localStorage.remove("auth_username");
  }

  getUsername(): string {
    return this.localStorage.get("auth_username");
  }

  getUserId(): number {
    return Number(this.localStorage.get("auth_user_id"));
  }
}


export function isLoggedin() {
  return localStorage.getItem("auth_token");
}
