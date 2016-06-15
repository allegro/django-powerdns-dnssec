import { Directive, ElementRef, Input } from "@angular/core";


@Directive({
  selector: "[highlight]",
  host: {
    "(mouseenter)": "onMouseEnter()",
    "(mouseleave)": "onMouseLeave()"
  }
})
export class HighlightDirective {

  @Input("highlight") highlightColor: string = "#d9edf7";

  private nativeElement: HTMLElement;

  constructor(el: ElementRef) {
    this.nativeElement = el.nativeElement;
  }

  private highlight(color: string) {
    this.nativeElement.style.backgroundColor = color;
  }

  onMouseEnter() {
    this.highlight(this.highlightColor);
  }

  onMouseLeave() {
    this.highlight(null);
  }
}
