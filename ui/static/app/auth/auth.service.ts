import { Injectable, Inject } from "@angular/core";
import { Http, Headers, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { LocalStorage } from "../local-storage";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";


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
          this.localStorage.set("is_admin", res.is_admin);
          return true;
        }
        return false;
      }).catch(this.handleError);
  }

  getToken(): string {
    return this.localStorage.get("auth_token");
  }

  isLoggedIn(): boolean {
    return (this.localStorage.get("auth_token")) ? true : false;
  }

  logout() {
    this.localStorage.clear();
  }

  getUsername(): string {
    return this.localStorage.get("auth_username");
  }

  getUserId(): number {
    return Number(this.localStorage.get("auth_user_id"));
  }

  isAdmin(): boolean {
    return (this.localStorage.get("is_admin") === "true");
  }

  private handleError(response: any) {
    if (response.status === 400 || response.status === 412) {
      return Observable.throw(JSON.parse(response._body));
    }
    let errMsg = response.message || "Server error";
    console.error(errMsg);
    return Observable.throw(errMsg);
  }
}


export function isLoggedin() {
  return localStorage.getItem("auth_token");
}
