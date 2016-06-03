import { Directive, ElementRef, OnInit } from "@angular/core";

declare var $: any;


@Directive({
  selector: "[tooltip]"
})
export class TooltipDirective implements OnInit {

  constructor(private el: ElementRef) { }

  public ngOnInit() {
    $(this.el.nativeElement).tooltip();
  }
}
