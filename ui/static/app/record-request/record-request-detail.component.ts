import { Component, OnInit } from "@angular/core";
import { ROUTER_DIRECTIVES, CanActivate, RouteParams, Router } from "@angular/router-deprecated";
import { isLoggedin }  from "../auth/auth.service";
import { Domain } from "../domain/domain";
import { DomainService } from "../domain/domain.service";
import { Record } from "../record/record";
import { RecordService } from "../record/record.service";
import { RecordRequestService } from "./record-request.service";
import { RecordRequest } from "./record-request";


declare var $: any;


@Component({
  templateUrl: "/static/app/record-request/record-request-detail.component.html",
  providers: [DomainService, RecordService, RecordRequestService],
  directives: [ROUTER_DIRECTIVES],
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
  showAutoAcceptanceMessage: boolean = false;
  backUrlParams: {[key: string]: string} = {};

  constructor(
    private routeParams: RouteParams,
    private router: Router,
    private recordRequestService: RecordRequestService,
    private domainService: DomainService,
    private recordService: RecordService
  ) { }

  getValue(fieldName: string): string {
    if ($.isEmptyObject(this.recordRequest.last_change)) {
      let value: string = this.recordRequest[`target_${fieldName}`];
      return `<span class="new">${value}</span>`;
    }

    let newValue: string = String(
      this.recordRequest.last_change[fieldName]["new"]
    );
    let oldValue: string = String(
      this.recordRequest.last_change[fieldName]["old"]
    );

    if (oldValue === newValue) {
      return `<span>${newValue}</span>`;
    } else {
      let result: string = "";
      if (this.recordRequest.last_change["_request_type"] === "update") {
        result += `<span class="old">${oldValue}</span> ->`;
      }
      return result + `<span class="new">${newValue}</span>`;
    }
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
    let backUrl: string = this.routeParams.get("backUrl");
    if (backUrl && backUrl.length > 0) {
      this.backUrlParams = JSON.parse(backUrl);
    }

    let requestId: any = this.routeParams.get("id");
    let showAutoAcceptanceMessage: string = this.routeParams.get("showAutoAcceptanceMessage");
    if (requestId) {
      this.recordRequestService.getRequestById(
        String(requestId)
      ).subscribe(
        (recordRequest) => {
          this.recordRequest = recordRequest;
          this.getDomain();
          this.getRecord();
          if (showAutoAcceptanceMessage === "true") {
            this.showAutoAcceptanceMessage = true;
          }
        }
      );
    }
  }

  onSelectRecord(record: Record) {
    this.router.navigate(["RecordDetail", { id: record.id }]);
  }

  onBack() {
    this.router.navigate(["RecordRequests", this.backUrlParams]);
  }
}
