import { Injectable } from "@angular/core";


@Injectable()
export class ConfigService {

  public apiDomain: string = "/api/v2/domains/";
  public apiRecord: string = "/api/v2/records/";
  public apiRecordRequest: string = "/api/v2/record-requests/";
}
