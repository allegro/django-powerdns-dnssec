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
  public modified: string;
  public record_request_id: number;
  public change_request: string;
  public delete_request: string;

  public static recordTypes: Array<{0: string, 1: string}> = [
    ["A", "IPv4 address: e.g. example.com -> 1.2.3.4"],
    ["CNAME", "alias: e.g. www.example.com -> example.com"],
    ["MX", "mail exchange: e.g. mx.example.com -> 1.2.3.4 "],
    ["TXT", "text: e.g. example.com -> \"description here\""],
    ["SRV", "service locator: e.g. _xmpp-client._tcp.example.com -> 0 5222 jabber.example.com"]
  ];

  constructor() { }

}
