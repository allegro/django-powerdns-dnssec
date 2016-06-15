import { Injectable } from "@angular/core";


// Raven and ravenEnabled variables from ui/templates/ui/index.html
declare var Raven: any;
declare var ravenEnabled: any;


@Injectable()
export class CustomExceptionHandler {

  call(exception: any, stackTrace?: any, reason?: string): void {
    if (ravenEnabled) {
      Raven.captureException(exception);
    } else {
      console.error(exception, stackTrace, reason);
    }
  }
}
