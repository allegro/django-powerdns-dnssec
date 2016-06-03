import { Component, OnInit } from "@angular/core";
import { URLSearchParams } from "@angular/http";
import { CanActivate, Router, RouteParams } from "@angular/router-deprecated";
import { AuthService, isLoggedin }  from "../auth/auth.service";
import { RecordRequest } from "./record-request";
import { RecordRequestService } from "./record-request.service";


@Component({
  templateUrl: "/static/app/templates/record-request.component.html",
  providers: [RecordRequestService],
  styles: [".panel-heading {overflow:hidden;}"]
})
@CanActivate(() => isLoggedin())
export class RecordRequestComponent implements OnInit {

  recordRequests: RecordRequest;
  state: string = "pending";
  errorMessage: string;

  constructor(
    private router: Router,
    private recordRequestService: RecordRequestService
  ) { }

  ngOnInit() {
    let search: URLSearchParams = new URLSearchParams();
    search.set("state", "1");
    this.recordRequestService.getRequests(search).map(
      (response) => response.json()
    ).subscribe(
      (json) => this.recordRequests = json.results
    );
  }

  onSelect(request: RecordRequest) {
    this.router.navigate(["RecordRequestDetail", { id: request.id }]);
  }

  onSelectShowRequest(show: string) {
    let search: URLSearchParams = new URLSearchParams();
    this.state = show;
    if (show === "accepted") {
      search.set("state", "2");
    } else if (show === "rejected") {
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
}
