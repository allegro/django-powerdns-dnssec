import { Component, OnInit } from "@angular/core";
import { URLSearchParams } from "@angular/http";
import { CanActivate, Router, RouteParams } from "@angular/router-deprecated";
import { AuthService, isLoggedin }  from "../auth/auth.service";
import { RecordRequest } from "./record-request";
import { RecordRequestService } from "./record-request.service";
import { HighlightDirective } from "../directives/highlight.directive";
import { ConfigService } from "../config.service";

@Component({
  templateUrl: "/static/app/record-request/record-request.component.html",
  providers: [RecordRequestService],
  directives: [HighlightDirective],
  styles: [`
    .panel-heading {overflow:hidden;}
    .wrap { text-overflow:ellipsis;overflow:hidden;white-space:nowrap;max-width:200px; }
    td { font-size:13px; }
    th { font-size:14px; }
  `]
})
@CanActivate(() => isLoggedin())
export class RecordRequestComponent implements OnInit {

  recordRequests: RecordRequest;
  state: string = "pending";
  errorMessage: string;
  jiraUrl: string = ConfigService.get("jiraUrl");

  constructor(
    private router: Router,
    private recordRequestService: RecordRequestService,
    private routeParams: RouteParams
  ) { }

  ngOnInit() {
    let state: string = this.routeParams.get("state");
    this.state = (state) ? state : "pending";
    this.getRecordRequest();
  }

  onSelect(request: RecordRequest) {
    this.router.navigate(
      ["RecordRequestDetail", {
        id: request.id,
        backUrl: JSON.stringify(this.routeParams.params)
      }]
    );
  }

  getRecordRequest() {
    let search: URLSearchParams = new URLSearchParams();
    if (this.state === "accepted") {
      search.set("state", "2");
    } else if (this.state === "rejected") {
      search.set("state", "3");
    } else {
      search.set("state", "1");
    }
    this.recordRequestService.getRequests(search).map(
      (response) => response.json()
    ).subscribe(
      (json) => this.recordRequests = json.results
    );
  }

  onSelectShowRequest(show: string) {
    this.state = show;
    this.router.navigate(["RecordRequests", { state: this.state }]);
  }
}
