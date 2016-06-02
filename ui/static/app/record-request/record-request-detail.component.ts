import { Component, OnInit } from "@angular/core";
import { CanActivate, RouteParams } from "@angular/router-deprecated";
import { isLoggedin }  from "../auth/auth.service";
import { RecordRequestService } from "./record-request.service";
import { RecordRequest } from "./record-request";


@Component({
  templateUrl: "/static/app/templates/record-request-detail.component.html",
  providers: [RecordRequestService],
})
@CanActivate(() => isLoggedin())
export class RecordRequestDetailComponent implements OnInit {

  recordRequest: RecordRequest;

  constructor(
    private routeParams: RouteParams,
    private recordRequestService: RecordRequestService
  ) { }

  ngOnInit() {
    let requestId: any = this.routeParams.get("id");
    if (requestId) {
      this.recordRequestService.getRequestById(
        String(requestId)
      ).subscribe(
        (recordRequest) => this.recordRequest = recordRequest
      );
    }
  }
}
