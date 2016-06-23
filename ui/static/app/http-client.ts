import { Injectable } from "@angular/core";
import { Http, Headers, URLSearchParams, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { AuthService } from "./auth/auth.service";


@Injectable()
export class HttpClient {

  apiToken: string;

  constructor(
    private http: Http,
    private authService: AuthService
  ) { }

  getAuthorizationHeader(): Headers {
    let headers: Headers = new Headers();
    headers.append("Content-Type", "application/json");
    headers.append("Authorization", `Token ${this.authService.getToken()}`);
    headers.append("Accept", "application/json; version=v2");
    return headers;
  }

  get(url: string, params?: URLSearchParams): Observable<Response>  {
    return this.http.get(url, {
      search: params,
      headers: this.getAuthorizationHeader()
    });
  }

  delete(url: string): Observable<Response>  {
    return this.http.delete(url, {
      headers: this.getAuthorizationHeader()
    });
  }

  post(url: string, data: string): Observable<Response> {
    return this.http.post(url, data, {
      headers: this.getAuthorizationHeader()
    });
  }

  patch(url: string, data: string): Observable<Response> {
    return this.http.patch(url, data, {
      headers: this.getAuthorizationHeader()
    });
  }
}
