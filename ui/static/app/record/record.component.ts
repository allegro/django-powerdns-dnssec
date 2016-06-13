import { Component, OnInit } from "@angular/core";
import { CanActivate, Router, RouteParams } from "@angular/router-deprecated";
import { URLSearchParams, HTTP_PROVIDERS } from "@angular/http";
import { AuthService, isLoggedin }  from "../auth/auth.service";
import { Record } from "./record";
import { RecordService } from "./record.service";
import { PaginationComponent } from "../pagination/pagination.component";
import { SearchComponent } from "../search.component";
import { HighlightDirective } from "../directives/highlight.directive";
import "rxjs/add/observable/throw";


@Component({
  templateUrl: "/static/app/templates/record.component.html",
  providers: [HTTP_PROVIDERS, RecordService],
  directives: [PaginationComponent, HighlightDirective],
  styles: [`
    .panel-heading {overflow:hidden;} td { cursor:pointer;}
    .legend { float:left;padding-top:5px; }
    .legend span {
      background-color: #dff0d8;width:20px;height:20px;
      border: 1px solid #ddd;margin-right:5px;
    }
    .read-only td { color:silver; cursor: not-allowed; }
  `]
})
@CanActivate(() => isLoggedin())
export class RecordComponent extends SearchComponent implements OnInit {

  records: Record[];
  errorMessage: any;
  currentOffset: number = 0;
  perPage: number = 100;
  totalCount: number;
  showAllRecords: boolean = false;
  activeUser: string;
  searchValue: string;
  additionalRouteParams: {[key: string]: string} = {
    "showAll": "false",
    "search": null
  };
  showResults: boolean = false;

  constructor(
    private router: Router,
    private routeParams: RouteParams,
    private recordService: RecordService,
    private authService: AuthService
  ) {
    super();
  }

  ngOnInit() {
    this.activeUser = this.authService.getUsername();
    this.showAllRecords = this.routeParams.get("showAll") === "true" ? true : false;
    this.additionalRouteParams["showAll"] = this.routeParams.get("showAll");
    let url_offset: string = this.routeParams.get("offset");
    this.currentOffset = url_offset ? Number(url_offset) : 0;
    this.searchValue = this.routeParams.get("search");
    this.getRecords();
  }

  search(value: string) {
    this.currentOffset = 0;
    if (value.length > 1) {
      this.searchValue = value;
      this.getRecords();
    } else {
      this.searchValue = null;
      this.getRecords();
    }
  }

  get isRecords(): boolean {
    if (typeof this.records === "object") {
      return this.records.length === 0 ? false : true;
    }
    return false;
  }

  getRecords() {
    this.showResults = false;
    let params: URLSearchParams = new URLSearchParams();
    params.set("limit", String(this.perPage));
    params.set("offset",  String(this.currentOffset));

    if (!this.showAllRecords) {
      params.set("owner", String(this.authService.getUserId()));
    }

    this.additionalRouteParams["search"] = this.searchValue;

    if (this.searchValue) {
      params.set("search", this.searchValue);
    }

    this.recordService.getRecords(params).map(
     (response) => response.json()
    ).subscribe((json) => {
      this.totalCount = json.count;
      this.records = json.results;
      this.showResults = true;
    }, error => this.errorMessage = <any>error);
  }

  onSelectShowAllRecords(show?: string) {
    if (show === "all") {
      this.additionalRouteParams["showAll"] = "true";
    } else {
      this.additionalRouteParams["showAll"] = "false";
    }
    this.router.navigate(["Records", this.additionalRouteParams]);
  }

  onSelect(record: Record) {
    if (record.type !== "PTR") {
      this.router.navigate(["RecordDetail", { id: record.id }]);
    }
  }

  deleteConfirm(record: Record) {
    if (confirm("Are you sure to delete this record: " + record.name)) {
      this.recordService.deleteRecord(record).subscribe((response) => {
        if (response.status === 204) {
          this.getRecords();
        }
      });
    }
  }
}
