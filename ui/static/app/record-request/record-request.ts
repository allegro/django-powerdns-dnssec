
export class RecordRequest {
  id: number;
  owner: string;
  target_name: string;
  target_type: string;
  target_content: string;
  target_prio: string;
  target_ttl: string;
  target_auth: string;
  target_remarks: string;
  created: string;
  domain: number;
  record: number;
  last_change: JSON;
  key: string;
}
