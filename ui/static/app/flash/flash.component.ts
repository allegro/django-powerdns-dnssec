import { Component } from "@angular/core";
import { FlashService } from "./flash.service";


@Component({
  selector: "flash-message",
  template: `
    <div *ngFor="let msg of messages; let i = index" class="alert alert-{{ msg[0] }}" role="alert">
      <button (click)="removeMessage(i)" type="button" class="close" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
      {{ msg[1] }}
    </div>
  `,
})
export class FlashComponent {

  messages: Array<{0: string, 1: string}> = [];

  constructor(private flashService: FlashService) {
    this.flashService.messages$.subscribe(
      message => this.messages.push(message)
    );
  }

  removeMessage(index: number) {
    this.messages.splice(index, 1);
  }

}
