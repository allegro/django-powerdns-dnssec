import { Injectable } from "@angular/core";


declare var globalConfig: {[key: string]: any};


@Injectable()
export class ConfigService {

  static get(key: string): any {
    return globalConfig[key];
  }
}
