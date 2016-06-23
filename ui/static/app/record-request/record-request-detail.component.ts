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
  templateUrl: "/static/app/record-request/record-request-detail.component.html",
  providers: [DomainService, RecordService, RecordRequestService],
  styles: [`
    td span { cursor:pointer; }
    :host >>> .new { color: green; }
    :host >>> .old { color: silver; }
  `]
})
@CanActivate(() => isLoggedin())
export class RecordRequestDetailComponent implements OnInit {

  domain: Domain;
  record: Record;
  recordRequest: RecordRequest;

  constructor(
    private routeParams: RouteParams,
    private router: Router,
    private recordRequestService: RecordRequestService,
    private domainService: DomainService,
    private recordService: RecordService
  ) { }

  getValue(fieldName: string): string {
    let recordRequestValue: string = String(
      this.recordRequest[`target_${fieldName}`]
    );
    if (!this.record) {
      return `<span>${recordRequestValue}`;
    }

    let recordValue: string = String(this.record[fieldName]);
    if (recordValue !== recordRequestValue) {
      return `
        <span class="old">${recordValue}</span> ->
        <span class="new">${recordRequestValue}</span>
      `;
    }
    return `<span>${recordRequestValue}</span>`;
  }

  getDomain() {
    this.domainService.getDomainById(
      this.recordRequest.domain
    ).subscribe(
      (domain) => this.domain = domain
    );
  }

  getRecord() {
    if (this.recordRequest.record) {
      this.recordService.getRecordById(
        String(this.recordRequest.record)
      ).subscribe(
        (record) => this.record = record
      );
    }
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
