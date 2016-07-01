import { AfterViewInit, Component, OnInit, ViewChild } from "@angular/core";
import { CanActivate, Router, RouteParams } from "@angular/router-deprecated";
import { URLSearchParams } from "@angular/http";
import { DomainService } from "./domain.service";
import { Domain } from "./domain";
import { isLoggedin }  from "../auth/auth.service";
import { SearchComponent } from "../search.component";
import { PaginationComponent } from "../pagination/pagination.component";
import { HighlightDirective } from "../directives/highlight.directive";
import "rxjs/add/observable/throw";

declare var $: any;


@Component({
  templateUrl: "/static/app/domain/domain.component.html",
  providers: [DomainService],
  directives: [PaginationComponent, HighlightDirective],
  styles: [`
    h1 small { font-size:14px; }
    td { font-size:13px; }
    th { font-size:14px; }
  `]
})
@CanActivate(() => isLoggedin())
export class DomainComponent extends SearchComponent implements OnInit {

  domains: Domain[];
  errorMessage: string;
  currentOffset: number = 0;
  perPage: number = 100;
  totalCount: number;
  searchValue: string = "";
  additionalRouteParams: {[key: string]: string} = {
    "search": null
  };
  @ViewChild("searchInput") searchInput;

  constructor(
    private domainService: DomainService,
    private router: Router,
    private routeParams: RouteParams
  ) {
    super();
  }

  ngOnInit() {
    let url_offset: string = this.routeParams.get("offset");
    this.currentOffset = url_offset ? Number(url_offset) : 0;
    let search: string = this.routeParams.get("search");
    this.searchValue = (search !== null) ? search : "";
    this.getDomains();
  }

  ngAfterViewInit() {
    $(this.searchInput.nativeElement).focus().get(0).setSelectionRange(
      this.searchValue.length, this.searchValue.length
    );
  }

  getDomains() {
    let params: URLSearchParams = new URLSearchParams();
    params.set("limit", String(this.perPage));
    params.set("offset", String(this.currentOffset));
    this.additionalRouteParams["search"] = this.searchValue;

    if (this.searchValue) {
      params.set("search", this.searchValue);
    }

    this.domainService.getDomains(params).map(
     (response) => response.json()
    ).subscribe(
      (json) => {
        this.totalCount = json.count;
        this.domains = json.results;
      },
      error => this.errorMessage = <any>error
    );
  }

  search(value: string) {
    this.currentOffset = 0;
    if (value.length > 1) {
      this.searchValue = value;
      this.getDomains();
    } else {
      this.searchValue = null;
      this.getDomains();
    }
  }
}
