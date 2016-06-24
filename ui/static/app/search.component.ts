
export abstract class SearchComponent {

  timer: any;

  abstract search(value: string): void;

  onKeyUpSearch(event: KeyboardEvent, value: string) {
    if (this.timer) {
      clearTimeout(this.timer);
    }
    this.timer = setTimeout(() => this.search(value), 400);
  }
}
