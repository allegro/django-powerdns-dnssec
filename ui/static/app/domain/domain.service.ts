import { Injectable } from "@angular/core";
import { URLSearchParams, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { HttpClient } from "../http-client";
import { AutocompleteServiceInterface } from "../autocomplete/autocomplete.service";
import { Domain } from "./domain";
import { ConfigService } from "../config.service";
import "rxjs/add/operator/catch";
import "rxjs/add/operator/map";


@Injectable()
export class DomainService implements AutocompleteServiceInterface {

  constructor(
    private http: HttpClient
  ) { }

  getDomains(search: URLSearchParams): Observable<Response> {
    let url: string = ConfigService.get("domainUrl");
    return this.http.get(url, search).catch(this.handleError);
  }

  getDomainById(id: number): Observable<Domain> {
    let url: string = `${ConfigService.get("domainUrl")}${id}/`;
    return this.http.get(url).map(
      response => {
        let json = response.json();
        return json || {};
      }
    ).catch(this.handleError);
  }

  getAutocompleteSearchResults(value: string): Observable<Domain[]> {
    let result: Array<{0: number, 1: string}> = [];
    let url: string =  ConfigService.get("domainUrl");
    let params: URLSearchParams = new URLSearchParams();
    params.set("name", value);
    params.set("limit", "10");
    return this.http.get(url, params).map(this.extractData).catch(this.handleError);
  }

  getAutocompleteCurrentValue(id: number): Observable<string> {
      let url: string = `${ConfigService.get("domainUrl")}${id}/`;
      return this.http.get(url).map(
        response => {
          let json = response.json();
          return json.name || "";
        }
      ).catch(this.handleError);
  }

  private extractData(res: Response) {
    if (res.status < 200 || res.status >= 300) {
      throw new Error("Bad response status: " + res.status);
    }
    let body = res.json();
    return body.results || [];
  }

  private handleError(error: any) {
    let errMsg = error.message || "Server error";
    console.error(errMsg);
    return Observable.throw(errMsg);
  }
}
