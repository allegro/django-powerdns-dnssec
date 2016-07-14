import { AfterViewInit, Component, Input } from "@angular/core";
import { AutocompleteServiceInterface } from "./autocomplete.service";


@Component({
  selector: "autocomplete",
  templateUrl: "/static/app/autocomplete/autocomplete.component.html",
  styles: [`
    a {cursor:pointer;}
    .empty-control { padding-top:8px; }
    .label {
      font-size:13px;padding:5px;padding-left:10px;padding-right:10px;margin-left: -9px;
      background-color: rgba(153, 153, 149, 0.22);color:rgba(0, 0, 0, 0.66);
    }
    .glyphicon { cursor:pointer }
    .read-only { padding-top: 10px; }
  `]
})
export class AutocompleteComponent implements AfterViewInit {
  @Input("placeholder") placeholder: string;
  @Input("service") service: AutocompleteServiceInterface;
  @Input("forNgModel") ngModel: any;
  @Input("ngModelField") ngModelField: string;
  @Input("readOnly") isReadOnly: boolean = false;
  @Input("afterSelectAction") afterSelectAction: Function;
  @Input("afterRemoveAction") afterRemoveAction: Function;

  activeIndex: number = 0;
  currentTextValue: string;
  selectValue: number;
  _value: string;
  showResults: boolean = false;
  showInput: boolean = true;
  showLabel: boolean = false;
  results: Array<{0: number, 1: string}>;
  startChar: number = 20; // [space] in ASCII
  endChar: number = 126; // ~ in ASCII

  ngAfterViewInit() {
    this.selectValue = this.ngModel[this.ngModelField];
    if (this.selectValue) {
      this.service.getAutocompleteCurrentValue(this.selectValue).subscribe(
        value => {
          this._value = value;
          this.showInput = false;
          this.showLabel = true;
        }
      );
    }
  }

  get value(): string {
    return this._value ? this._value : "";
  }

  onKey(event: KeyboardEvent, value: string) {
    if (event.keyCode === 27) {
      // escape
      this.showResults = false;
      return;
    } else if (event.keyCode === 38) {
      // key up
      this.prevActiveMatch();
      return;
    } else if (event.keyCode === 40) {
      // key down
      this.nextActiveMatch();
      return;
    }
    else if (event.keyCode === 13) {
      // enter
      this.onSelect(this.results[this.activeIndex]);
      event.preventDefault();
      return;
    }
    else if (
      event.keyCode < this.startChar ||
      event.keyCode > this.endChar &&
      event.keyCode !== 8
    )

    this.activeIndex = 0;
    if (value.length >= 2) {
      this.service.getAutocompleteSearchResults(value).subscribe(
        response => {
          this.results = [];
          for (let item in response) {
            this.results.push([response[item].id, response[item].name]);
          }
          if (this.results.length > 0) {
            this.showResults = true;
          } else {
            this.showResults = false;
          }
        }
      );
    } else {
      this.showResults = false;
    }
  }

  prevActiveMatch() {
    let index: number = this.activeIndex;
    this.activeIndex = index - 1 < 0 ? this.results.length - 1 : index - 1;
  }

  nextActiveMatch() {
    let index: number = this.activeIndex;
    this.activeIndex = index + 1 > this.results.length - 1 ? 0 : index + 1;
  }

  isActive(item: {0: number, 1: string}): boolean {
    return this.activeIndex === this.results.indexOf(item) ? true : false;
  }

  selectActive(item: {0: number, 1: string}) {
    this.activeIndex = this.results.indexOf(item);
  }

  removeCurrent() {
    this.showInput = true;
    this.showLabel = false;
    this.ngModel[this.ngModelField] = null;
    this.currentTextValue = "";
    if (this.afterRemoveAction) {
      this.afterRemoveAction();
    }
  }

  onSelect(item: {0: number, 1: string}) {
    this.showResults = false;
    this.selectValue = this.results[this.activeIndex][0];
    this._value = item[1];
    this.ngModel[this.ngModelField] = item[0];
    this.results = [];
    this.showInput = false;
    this.showLabel = true;

    if (this.afterSelectAction) {
      this.afterSelectAction();
    }
  }
}
