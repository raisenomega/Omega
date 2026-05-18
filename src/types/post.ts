// Temporary type until types.ts is regenerated
export interface Post {
  id: string;
  organization_id: string;
  title: string;
  body: string;
  platform: string;
  status: string;
  scheduled_at: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}
