import { Injectable } from "@angular/core";
import { ConfigService } from "./config.service";


// Raven and ravenEnabled variables from ui/templates/ui/index.html
declare var Raven: any;


@Injectable()
export class CustomExceptionHandler {

  call(exception: any, stackTrace?: any, reason?: string): void {
    if (ConfigService.get("ravenEnabled")) {
      Raven.captureException(exception);
    } else {
      console.error(exception, stackTrace, reason);
    }
  }
}
