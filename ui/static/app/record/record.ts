import { Domain } from "../domain/domain";


export class Record {
  public id: number;
  public domain: number;
  public name: string;
  public content: string;
  public type: string;
  public remarks: string;
  public prio: number;
  public ttl: number = 3600;
  public owner: string;

  public static recordTypes: Array<string> = [
    "A", "CNAME", "MX", "TXT", "SRV"
  ];

  constructor() { }

}
