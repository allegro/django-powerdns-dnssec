import { Component, OnInit } from "@angular/core";
import { CanActivate, Router, RouteParams } from "@angular/router-deprecated";
import { URLSearchParams } from "@angular/http";
import { DomainService } from "./domain.service";
import { Domain } from "./domain";
import { isLoggedin }  from "../auth/auth.service";
import { PaginationComponent } from "../pagination/pagination.component";
import "rxjs/add/observable/throw";


@Component({
  templateUrl: "/static/app/templates/domain.component.html",
  providers: [DomainService],
  directives: [PaginationComponent]
})
@CanActivate(() => isLoggedin())
export class DomainComponent implements OnInit {

  domains: Domain[];
  errorMessage: string;
  currentOffset: number = 0;
  perPage: number = 20;
  totalCount: number;

  constructor(
    private domainService: DomainService,
    private router: Router,
    private routeParams: RouteParams
  ) { }

  ngOnInit() {
    let params: URLSearchParams = new URLSearchParams();
    this.currentOffset = Number(this.routeParams.get("offset"));
    params.set("limit", String(this.perPage));
    params.set("offset",  String(this.currentOffset));

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
}
