import { Injectable } from "@angular/core";
import { Subject }    from "rxjs/Subject";


@Injectable()
export class FlashService {

  private messageSource = new Subject<{0: string, 1: string}>();

  messages$ = this.messageSource.asObservable();

  addMessage(message: {0: string, 1: string}) {
    this.messageSource.next(message);
  }
}
