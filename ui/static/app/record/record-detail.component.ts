import { Component, OnInit } from "@angular/core";
import { FormBuilder, FORM_DIRECTIVES, Control, ControlGroup, Validators } from "@angular/common";
import { CanActivate, Router, RouteParams } from "@angular/router-deprecated";
import { HTTP_PROVIDERS } from "@angular/http";
import { AuthService } from "../auth/auth.service";
import { TooltipDirective } from "../tooltip.directive";
import { AutocompleteComponent } from "../autocomplete/autocomplete.component";
import { DomainService } from "../domain/domain.service";
import { RecordService } from "./record.service";
import { Record } from "./record";
import { isLoggedin }  from "../auth/auth.service";
import "rxjs/add/observable/throw";


@Component({
  templateUrl: "/static/app/templates/record-detail.component.html",
  providers: [HTTP_PROVIDERS, RecordService, DomainService],
  directives: [FORM_DIRECTIVES, AutocompleteComponent, TooltipDirective],
  styles: [".ng-invalid { border-color:#ebccd1;}"]
})
@CanActivate(() => isLoggedin())
export class RecordDetailComponent implements OnInit {

    record: Record;
    errorMessage: any;
    isCreate: boolean = true;
    recordTypes: Array<string> = Record.recordTypes;
    recordForm: ControlGroup;
    save: boolean = false;
    isMxRecord: boolean = false;

    constructor(
      private router: Router,
      private routeParams: RouteParams,
      private recordService: RecordService,
      private domainService: DomainService,
      private authService: AuthService,
      private formBuilder: FormBuilder
    ) {
        this.recordForm = formBuilder.group({
          name: ["", Validators.required],
          content: ["", Validators.required],
          type: ["", Validators.required],
          ttl: ["", Validators.required],
          prio: [], // Visible only if type is MX
          remarks: []
        });
    }

    ngOnInit() {
      let recordId: any = this.routeParams.get("id");
      if (!recordId) {
        this.record = new Record();
        this.record.owner = this.authService.getUsername();
        this.isCreate = true;
      } else {
        this.isCreate = false;
        this.recordService.getRecordById(
          String(recordId)
        ).subscribe(
          record => {
            this.record = record;
            this.isMxRecord = (record.type === "MX") ? true : false;
          },
          error => this.errorMessage = <any>error
        );
      }
    }

    onSubmit() {
      if (this.recordForm.valid) {
        this.recordService.updateOrCreateRecord(this.record).subscribe(
          record => {
            this.router.navigate(["Records"]);
          },
          error => this.errorMessage = <any>error
        );
      } else {
        this.save = false;
      }
    }

    onChangeType(value: string) {
      if (value === "MX") {
        this.isMxRecord = true;
      } else {
        this.isMxRecord = false;
      }
    }
}
