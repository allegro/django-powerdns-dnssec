import { Component, OnInit } from "@angular/core";
import { CanActivate, RouteParams, Router } from "@angular/router-deprecated";
import { isLoggedin }  from "../auth/auth.service";
import { Domain } from "../domain/domain";
import { DomainService } from "../domain/domain.service";
import { Record } from "../record/record";
import { RecordService } from "../record/record.service";
import { RecordRequestService } from "./record-request.service";
import { RecordRequest } from "./record-request";


@Component({
  templateUrl: "/static/app/templates/record-request-detail.component.html",
  providers: [DomainService, RecordService, RecordRequestService],
  styles: ["td span { cursor:pointer; }"]
})
@CanActivate(() => isLoggedin())
export class RecordRequestDetailComponent implements OnInit {

  recordRequest: RecordRequest;
  domain: Domain;
  record: Record;

  constructor(
    private routeParams: RouteParams,
    private router: Router,
    private recordRequestService: RecordRequestService,
    private domainService: DomainService,
    private recordService: RecordService
  ) { }

  getDomain() {
    this.domainService.getDomainById(this.recordRequest.domain).subscribe(
      (domain) => this.domain = domain
    );
  }

  getRecord() {
    this.recordService.getRecordById(
      String(this.recordRequest.record)
    ).subscribe(
      (record) => this.record = record
    );
  }

  ngOnInit() {
    let requestId: any = this.routeParams.get("id");
    if (requestId) {
      this.recordRequestService.getRequestById(
        String(requestId)
      ).subscribe(
        (recordRequest) => {
          this.recordRequest = recordRequest;
          this.getDomain();
          this.getRecord();
        }
      );
    }
  }

  onSelectRecord(record: Record) {
   this.router.navigate(["RecordDetail", { id: record.id }]);
  }
}
