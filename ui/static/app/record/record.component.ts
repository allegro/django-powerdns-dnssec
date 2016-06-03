import { Component, OnInit } from "@angular/core";
import { CanActivate, Router, RouteParams } from "@angular/router-deprecated";
import { URLSearchParams, HTTP_PROVIDERS } from "@angular/http";
import { RecordService } from "./record.service";
import { Record } from "./record";
import { AuthService, isLoggedin }  from "../auth/auth.service";
import { PaginationComponent } from "../pagination/pagination.component";
import "rxjs/add/observable/throw";


@Component({
  templateUrl: "/static/app/templates/record.component.html",
  providers: [HTTP_PROVIDERS, RecordService],
  directives: [PaginationComponent],
  styles: [`
    .panel-heading {overflow:hidden;} td { cursor:pointer;}
    .legend {float:left;padding-top:5px;}
    .legend span {
      background-color: #dff0d8;width:20px;height:20px;
      border: 1px solid #ddd;margin-right:5px;
    }
  `]
})
@CanActivate(() => isLoggedin())
export class RecordComponent implements OnInit {

  records: Record[];
  errorMessage: any;
  currentOffset: number = 0;
  perPage: number = 20;
  totalCount: number;
  showAllRecords: boolean = false;
  activeUser: string;
  additionalRouteParams: {[key: string]: string} = {"showAll": "false"};

  constructor(
    private router: Router,
    private routeParams: RouteParams,
    private recordService: RecordService,
    private authService: AuthService
  ) { }

  ngOnInit() {
    this.activeUser = this.authService.getUsername();
    this.showAllRecords = this.routeParams.get("showAll") === "true" ? true : false;
    this.additionalRouteParams["showAll"] = this.routeParams.get("showAll");
    this.getRecords();
  }

  getRecords() {
    let params: URLSearchParams = new URLSearchParams();
    this.currentOffset = Number(this.routeParams.get("offset"));
    params.set("limit", String(this.perPage));
    params.set("offset",  String(this.currentOffset));

    if (!this.showAllRecords) {
      params.set("owner", String(this.authService.getUserId()));
    }

    this.recordService.getRecords(params).map(
     (response) => response.json()
    ).subscribe((json) => {
      this.totalCount = json.count;
      this.records = json.results;
    }, error => this.errorMessage = <any>error);
  }

  onSelectShowAllRecords(show?: string) {
    if (show === "all") {
      this.showAllRecords = true;
      this.additionalRouteParams["showAll"] = "true";
    } else {
      this.additionalRouteParams["showAll"] = "false";
      this.showAllRecords = false;
    }
    this.getRecords();
  }

  onSelect(record: Record) {
    this.router.navigate(["RecordDetail", { id: record.id }]);
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
