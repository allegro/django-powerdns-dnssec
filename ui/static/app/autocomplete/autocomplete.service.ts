import { Observable } from "rxjs/Observable";

export interface AutocompleteServiceInterface {
  getAutocompleteSearchResults(value: string): Observable<any[]>;
  getAutocompleteCurrentValue(id: number): Observable<string> ;
}
