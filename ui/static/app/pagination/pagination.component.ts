import { Component, Input } from "@angular/core";
import { Router } from "@angular/router-deprecated";


@Component({
  selector: "pagination",
  template: `
    <div class="text-center" *ngIf="totalCount && totalCount > perPage">
      <nav>
        <ul class="pagination pagination-sm">
          <li [style.display]="showPrev ? 'inline' : 'none'">
            <a (click)="onSelect(prevOffset)" aria-label="Previous">
              <span aria-hidden="true">&laquo;</span>
            </a>
          </li>
          <li *ngIf="pages[0][1] > 1">
            <a>...</a>
          </li>
          <li *ngFor="let page of pages" [class.active]="page[0] == currentOffset">
            <a (click)="onSelect(page[0])">{{ page[1] }}</a>
          </li>
          <li *ngIf="pages[pages.length - 1][1] < allPages">
            <a>...</a>
          </li>
          <li [style.display]="showNext ? 'inline' : 'none'">
            <a (click)="onSelect(nextOffset)" aria-label="Next">
              <span aria-hidden="true">&raquo;</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  `,
  styles: ["a { cursor:pointer; }"],
})
export class PaginationComponent {
  @Input() totalCount: number;
  @Input() perPage: number;
  @Input() currentOffset: number;
  @Input() routeName: string;
  @Input() additionalRouteParams: {[key: string]: string} = {};

  allPages: number;
  nextOffset: number = 0;
  prevOffset: number = 0;
  showNext: boolean = false;
  showPrev: boolean = false;

  constructor(private router: Router) { }

  get pages(): Array<{0: number, 1: number}> {
    let result: Array<{0: number, 1: number}> = [];
    let startPage: number = 1;
    let totalPage: number = Number(Math.ceil(this.totalCount / this.perPage));
    this.allPages = totalPage;
    let paginationLimit: number = 5;

    if (totalPage > paginationLimit) {
      let currentPage: number = 1;
      if (this.currentOffset !== 0) {
        currentPage = Math.ceil(this.currentOffset / this.perPage + 1);
      }
      startPage = currentPage - Math.floor(paginationLimit / 2);
      if (startPage < 1) {
        startPage = 1;
      }
      let endPage: number = startPage + paginationLimit - 1 ;
      if (endPage < totalPage) {
        totalPage = endPage;
      } else {
        startPage = totalPage - (paginationLimit - 1);
      }
    }

    for (let i: number = startPage; i <= totalPage; i++) {
      let offset: number = (i - 1) * this.perPage;
      result.push([offset, i]);
    }

    this.showPrev = true;
    this.showNext = true;
    this.nextOffset = this.currentOffset + this.perPage;
    this.prevOffset = this.currentOffset - this.perPage;

    if (this.prevOffset < 0) {
      this.showPrev = false;
    }

    if (this.nextOffset >= this.totalCount) {
      this.showNext = false;
    }
    return result;
  }

  onSelect(offset: number) {
    this.additionalRouteParams["offset"] = String(offset);
    this.router.navigate([this.routeName, this.additionalRouteParams]);
  }
}
