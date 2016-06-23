import { Injectable } from "@angular/core";
import { URLSearchParams, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { ConfigService } from "../config.service";
import { RecordRequest } from "./record-request";
import { HttpClient } from "../http-client";
import { AuthService } from "../auth/auth.service";
import "rxjs/add/operator/catch";
import "rxjs/add/operator/map";


@Injectable()
export class RecordRequestService {

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  getRequests(search: URLSearchParams): Observable<Response> {
    search.set("owner", String(this.authService.getUserId()));
    let url: string = ConfigService.get("recordRequestUrl");
    return this.http.get(url, search).catch(this.handleError);
  }

  getRequestById(id: string): Observable<RecordRequest> {
    let url: string = `${ConfigService.get("recordRequestUrl")}${id}/`;
    return this.http.get(url).map(
        this.extractSingleData
    ).catch(this.handleError);
  }

  private extractSingleData(res: Response) {
    if (res.status < 200 || res.status >= 300) {
        throw new Error("Bad response status: " + res.status);
    }
    let body = res.json();
    return body || {};
  }

  private handleError(response: any) {
    let errMsg = response.message || "Server error";
    console.error(errMsg);
    return Observable.throw(errMsg);
  }
}
