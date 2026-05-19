export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          extensions?: Json
          operationName?: string
          query?: string
          variables?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      agent_log: {
        Row: {
          agent_code: string
          cache_hit: boolean | null
          client_id: string | null
          cost_usd: number | null
          created_at: string
          error_message: string | null
          id: string
          input_tokens: number | null
          latency_ms: number | null
          model_used: string
          output_tokens: number | null
          request_id: string | null
          status: string
          user_id: string | null
        }
        Insert: {
          agent_code: string
          cache_hit?: boolean | null
          client_id?: string | null
          cost_usd?: number | null
          created_at?: string
          error_message?: string | null
          id?: string
          input_tokens?: number | null
          latency_ms?: number | null
          model_used: string
          output_tokens?: number | null
          request_id?: string | null
          status: string
          user_id?: string | null
        }
        Update: {
          agent_code?: string
          cache_hit?: boolean | null
          client_id?: string | null
          cost_usd?: number | null
          created_at?: string
          error_message?: string | null
          id?: string
          input_tokens?: number | null
          latency_ms?: number | null
          model_used?: string
          output_tokens?: number | null
          request_id?: string | null
          status?: string
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "agent_log_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
      agent_memory: {
        Row: {
          agent_code: string
          client_id: string | null
          confidence: number
          context: string
          created_at: string
          decision: string
          embedding: string | null
          evaluated_at: string | null
          id: string
          memory_type: string
          metadata: Json | null
          outcome: string | null
          reasoning: string | null
          reseller_id: string | null
          user_id: string | null
          was_correct: boolean | null
        }
        Insert: {
          agent_code: string
          client_id?: string | null
          confidence: number
          context: string
          created_at?: string
          decision: string
          embedding?: string | null
          evaluated_at?: string | null
          id?: string
          memory_type: string
          metadata?: Json | null
          outcome?: string | null
          reasoning?: string | null
          reseller_id?: string | null
          user_id?: string | null
          was_correct?: boolean | null
        }
        Update: {
          agent_code?: string
          client_id?: string | null
          confidence?: number
          context?: string
          created_at?: string
          decision?: string
          embedding?: string | null
          evaluated_at?: string | null
          id?: string
          memory_type?: string
          metadata?: Json | null
          outcome?: string | null
          reasoning?: string | null
          reseller_id?: string | null
          user_id?: string | null
          was_correct?: boolean | null
        }
        Relationships: [
          {
            foreignKeyName: "agent_memory_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "agent_memory_reseller_id_fkey"
            columns: ["reseller_id"]
            isOneToOne: false
            referencedRelation: "resellers"
            referencedColumns: ["id"]
          },
        ]
      }
      agents: {
        Row: {
          category: string
          code: string
          config: Json | null
          created_at: string
          description: string | null
          id: string
          is_active: boolean
          is_premium: boolean
          model_tier: string
          name: string
          system_prompt: string | null
          updated_at: string
        }
        Insert: {
          category: string
          code: string
          config?: Json | null
          created_at?: string
          description?: string | null
          id?: string
          is_active?: boolean
          is_premium?: boolean
          model_tier: string
          name: string
          system_prompt?: string | null
          updated_at?: string
        }
        Update: {
          category?: string
          code?: string
          config?: Json | null
          created_at?: string
          description?: string | null
          id?: string
          is_active?: boolean
          is_premium?: boolean
          model_tier?: string
          name?: string
          system_prompt?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      analytics_events: {
        Row: {
          client_id: string
          event_data: Json | null
          event_type: string
          id: string
          metric_value: number | null
          occurred_at: string
          platform: string
          scheduled_post_id: string | null
        }
        Insert: {
          client_id: string
          event_data?: Json | null
          event_type: string
          id?: string
          metric_value?: number | null
          occurred_at?: string
          platform: string
          scheduled_post_id?: string | null
        }
        Update: {
          client_id?: string
          event_data?: Json | null
          event_type?: string
          id?: string
          metric_value?: number | null
          occurred_at?: string
          platform?: string
          scheduled_post_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "analytics_events_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "analytics_events_scheduled_post_id_fkey"
            columns: ["scheduled_post_id"]
            isOneToOne: false
            referencedRelation: "scheduled_posts"
            referencedColumns: ["id"]
          },
        ]
      }
      anti_fraud_signals: {
        Row: {
          auto_blocked: boolean
          client_id: string | null
          detected_at: string
          id: string
          metadata: Json
          resolution_note: string | null
          resolved: boolean
          resolved_at: string | null
          resolved_by: string | null
          severity: string
          signal_type: string
          signal_value: string
        }
        Insert: {
          auto_blocked?: boolean
          client_id?: string | null
          detected_at?: string
          id?: string
          metadata?: Json
          resolution_note?: string | null
          resolved?: boolean
          resolved_at?: string | null
          resolved_by?: string | null
          severity?: string
          signal_type: string
          signal_value: string
        }
        Update: {
          auto_blocked?: boolean
          client_id?: string | null
          detected_at?: string
          id?: string
          metadata?: Json
          resolution_note?: string | null
          resolved?: boolean
          resolved_at?: string | null
          resolved_by?: string | null
          severity?: string
          signal_type?: string
          signal_value?: string
        }
        Relationships: [
          {
            foreignKeyName: "anti_fraud_signals_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
      brand_files: {
        Row: {
          client_id: string
          file_type: string
          filename: string
          id: string
          size_bytes: number | null
          storage_path: string
          uploaded_at: string
        }
        Insert: {
          client_id: string
          file_type: string
          filename: string
          id?: string
          size_bytes?: number | null
          storage_path: string
          uploaded_at?: string
        }
        Update: {
          client_id?: string
          file_type?: string
          filename?: string
          id?: string
          size_bytes?: number | null
          storage_path?: string
          uploaded_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "brand_files_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
      client_plans: {
        Row: {
          addons: Json
          client_id: string
          created_at: string
          current_period_end: string
          current_period_start: string
          id: string
          plan: string
          stripe_subscription_id: string | null
          updated_at: string
        }
        Insert: {
          addons?: Json
          client_id: string
          created_at?: string
          current_period_end: string
          current_period_start?: string
          id?: string
          plan: string
          stripe_subscription_id?: string | null
          updated_at?: string
        }
        Update: {
          addons?: Json
          client_id?: string
          created_at?: string
          current_period_end?: string
          current_period_start?: string
          id?: string
          plan?: string
          stripe_subscription_id?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "client_plans_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: true
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
      clients: {
        Row: {
          brand_voice: Json | null
          business_type: string | null
          created_at: string
          description: string | null
          device_fingerprint: string | null
          id: string
          industry: string | null
          name: string
          plan: string
          reseller_id: string
          status: string
          target_audience: Json | null
          updated_at: string
          user_id: string | null
        }
        Insert: {
          brand_voice?: Json | null
          business_type?: string | null
          created_at?: string
          description?: string | null
          device_fingerprint?: string | null
          id?: string
          industry?: string | null
          name: string
          plan?: string
          reseller_id: string
          status?: string
          target_audience?: Json | null
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          brand_voice?: Json | null
          business_type?: string | null
          created_at?: string
          description?: string | null
          device_fingerprint?: string | null
          id?: string
          industry?: string | null
          name?: string
          plan?: string
          reseller_id?: string
          status?: string
          target_audience?: Json | null
          updated_at?: string
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "clients_reseller_id_fkey"
            columns: ["reseller_id"]
            isOneToOne: false
            referencedRelation: "resellers"
            referencedColumns: ["id"]
          },
        ]
      }
      content_lab_generated: {
        Row: {
          agent_code: string
          brand_voice_score: number | null
          client_id: string
          compliance_passed: boolean | null
          confidence: number | null
          content_type: string
          created_at: string
          generated_text: string | null
          id: string
          media_urls: Json | null
          metadata: Json | null
          prompt: string | null
          status: string
          sub_brand_id: string | null
          updated_at: string
        }
        Insert: {
          agent_code: string
          brand_voice_score?: number | null
          client_id: string
          compliance_passed?: boolean | null
          confidence?: number | null
          content_type: string
          created_at?: string
          generated_text?: string | null
          id?: string
          media_urls?: Json | null
          metadata?: Json | null
          prompt?: string | null
          status?: string
          sub_brand_id?: string | null
          updated_at?: string
        }
        Update: {
          agent_code?: string
          brand_voice_score?: number | null
          client_id?: string
          compliance_passed?: boolean | null
          confidence?: number | null
          content_type?: string
          created_at?: string
          generated_text?: string | null
          id?: string
          media_urls?: Json | null
          metadata?: Json | null
          prompt?: string | null
          status?: string
          sub_brand_id?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "content_lab_generated_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "content_lab_generated_sub_brand_id_fkey"
            columns: ["sub_brand_id"]
            isOneToOne: false
            referencedRelation: "sub_brands"
            referencedColumns: ["id"]
          },
        ]
      }
      feature_usage: {
        Row: {
          client_id: string
          cost_usd: number | null
          feature_code: string
          id: string
          metadata: Json | null
          period_end: string | null
          period_start: string
          usage_count: number
        }
        Insert: {
          client_id: string
          cost_usd?: number | null
          feature_code: string
          id?: string
          metadata?: Json | null
          period_end?: string | null
          period_start: string
          usage_count?: number
        }
        Update: {
          client_id?: string
          cost_usd?: number | null
          feature_code?: string
          id?: string
          metadata?: Json | null
          period_end?: string | null
          period_start?: string
          usage_count?: number
        }
        Relationships: [
          {
            foreignKeyName: "feature_usage_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
      leads: {
        Row: {
          consent_date: string | null
          consent_given: boolean
          created_at: string
          email: string
          id: string
          name: string | null
          notes: string | null
          phone: string | null
          reseller_id: string
          source: string | null
          status: string
          updated_at: string
        }
        Insert: {
          consent_date?: string | null
          consent_given?: boolean
          created_at?: string
          email: string
          id?: string
          name?: string | null
          notes?: string | null
          phone?: string | null
          reseller_id: string
          source?: string | null
          status?: string
          updated_at?: string
        }
        Update: {
          consent_date?: string | null
          consent_given?: boolean
          created_at?: string
          email?: string
          id?: string
          name?: string | null
          notes?: string | null
          phone?: string | null
          reseller_id?: string
          source?: string | null
          status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "leads_reseller_id_fkey"
            columns: ["reseller_id"]
            isOneToOne: false
            referencedRelation: "resellers"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          avatar_url: string | null
          created_at: string
          email: string
          full_name: string | null
          id: string
          role: string
          updated_at: string
        }
        Insert: {
          avatar_url?: string | null
          created_at?: string
          email: string
          full_name?: string | null
          id: string
          role?: string
          updated_at?: string
        }
        Update: {
          avatar_url?: string | null
          created_at?: string
          email?: string
          full_name?: string | null
          id?: string
          role?: string
          updated_at?: string
        }
        Relationships: []
      }
      reseller_agents: {
        Row: {
          agent_id: string
          created_at: string
          custom_config: Json | null
          id: string
          is_enabled: boolean
          reseller_id: string
        }
        Insert: {
          agent_id: string
          created_at?: string
          custom_config?: Json | null
          id?: string
          is_enabled?: boolean
          reseller_id: string
        }
        Update: {
          agent_id?: string
          created_at?: string
          custom_config?: Json | null
          id?: string
          is_enabled?: boolean
          reseller_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "reseller_agents_agent_id_fkey"
            columns: ["agent_id"]
            isOneToOne: false
            referencedRelation: "agents"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "reseller_agents_reseller_id_fkey"
            columns: ["reseller_id"]
            isOneToOne: false
            referencedRelation: "resellers"
            referencedColumns: ["id"]
          },
        ]
      }
      reseller_branding: {
        Row: {
          created_at: string
          custom_css: string | null
          logo_url: string | null
          primary_color: string | null
          reseller_id: string
          secondary_color: string | null
          tagline: string | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          custom_css?: string | null
          logo_url?: string | null
          primary_color?: string | null
          reseller_id: string
          secondary_color?: string | null
          tagline?: string | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          custom_css?: string | null
          logo_url?: string | null
          primary_color?: string | null
          reseller_id?: string
          secondary_color?: string | null
          tagline?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "reseller_branding_reseller_id_fkey"
            columns: ["reseller_id"]
            isOneToOne: true
            referencedRelation: "resellers"
            referencedColumns: ["id"]
          },
        ]
      }
      resellers: {
        Row: {
          created_at: string
          custom_domain: string | null
          id: string
          name: string
          owner_user_id: string
          plan: string
          slug: string
          status: string
          stripe_account_id: string | null
          stripe_customer_id: string | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          custom_domain?: string | null
          id?: string
          name: string
          owner_user_id: string
          plan?: string
          slug: string
          status?: string
          stripe_account_id?: string | null
          stripe_customer_id?: string | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          custom_domain?: string | null
          id?: string
          name?: string
          owner_user_id?: string
          plan?: string
          slug?: string
          status?: string
          stripe_account_id?: string | null
          stripe_customer_id?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      scheduled_posts: {
        Row: {
          attempts: number
          client_id: string
          content_id: string | null
          created_at: string
          error_message: string | null
          id: string
          platform_post_id: string | null
          scheduled_for: string
          social_account_id: string | null
          status: string
          updated_at: string
        }
        Insert: {
          attempts?: number
          client_id: string
          content_id?: string | null
          created_at?: string
          error_message?: string | null
          id?: string
          platform_post_id?: string | null
          scheduled_for: string
          social_account_id?: string | null
          status?: string
          updated_at?: string
        }
        Update: {
          attempts?: number
          client_id?: string
          content_id?: string | null
          created_at?: string
          error_message?: string | null
          id?: string
          platform_post_id?: string | null
          scheduled_for?: string
          social_account_id?: string | null
          status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "scheduled_posts_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "scheduled_posts_content_id_fkey"
            columns: ["content_id"]
            isOneToOne: false
            referencedRelation: "content_lab_generated"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "scheduled_posts_social_account_id_fkey"
            columns: ["social_account_id"]
            isOneToOne: false
            referencedRelation: "social_accounts"
            referencedColumns: ["id"]
          },
        ]
      }
      social_accounts: {
        Row: {
          access_token: string | null
          account_id: string | null
          account_name: string
          client_id: string
          created_at: string
          expires_at: string | null
          id: string
          platform: string
          refresh_token: string | null
          status: string
          updated_at: string
        }
        Insert: {
          access_token?: string | null
          account_id?: string | null
          account_name: string
          client_id: string
          created_at?: string
          expires_at?: string | null
          id?: string
          platform: string
          refresh_token?: string | null
          status?: string
          updated_at?: string
        }
        Update: {
          access_token?: string | null
          account_id?: string | null
          account_name?: string
          client_id?: string
          created_at?: string
          expires_at?: string | null
          id?: string
          platform?: string
          refresh_token?: string | null
          status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "social_accounts_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
      stripe_webhook_events: {
        Row: {
          data: Json
          error_message: string | null
          id: string
          processed_at: string
          success: boolean | null
          type: string
        }
        Insert: {
          data: Json
          error_message?: string | null
          id: string
          processed_at?: string
          success?: boolean | null
          type: string
        }
        Update: {
          data?: Json
          error_message?: string | null
          id?: string
          processed_at?: string
          success?: boolean | null
          type?: string
        }
        Relationships: []
      }
      sub_brands: {
        Row: {
          brand_voice: Json | null
          client_id: string
          created_at: string
          description: string | null
          id: string
          name: string
          updated_at: string
        }
        Insert: {
          brand_voice?: Json | null
          client_id: string
          created_at?: string
          description?: string | null
          id?: string
          name: string
          updated_at?: string
        }
        Update: {
          brand_voice?: Json | null
          client_id?: string
          created_at?: string
          description?: string | null
          id?: string
          name?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "sub_brands_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
      training_pairs: {
        Row: {
          agent_code: string
          created_at: string
          curator_notes: string | null
          curator_user_id: string | null
          expected_output: string
          id: string
          input_context: string
          is_active: boolean
          quality_score: number | null
          source_memory_id: string | null
        }
        Insert: {
          agent_code: string
          created_at?: string
          curator_notes?: string | null
          curator_user_id?: string | null
          expected_output: string
          id?: string
          input_context: string
          is_active?: boolean
          quality_score?: number | null
          source_memory_id?: string | null
        }
        Update: {
          agent_code?: string
          created_at?: string
          curator_notes?: string | null
          curator_user_id?: string | null
          expected_output?: string
          id?: string
          input_context?: string
          is_active?: boolean
          quality_score?: number | null
          source_memory_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "training_pairs_source_memory_id_fkey"
            columns: ["source_memory_id"]
            isOneToOne: false
            referencedRelation: "agent_memory"
            referencedColumns: ["id"]
          },
        ]
      }
      upsell_requests: {
        Row: {
          agent_id: string | null
          amount_usd: number | null
          approved_at: string | null
          approved_by: string | null
          client_id: string
          created_at: string
          id: string
          requested_by: string | null
          status: string
          stripe_payment_intent_id: string | null
        }
        Insert: {
          agent_id?: string | null
          amount_usd?: number | null
          approved_at?: string | null
          approved_by?: string | null
          client_id: string
          created_at?: string
          id?: string
          requested_by?: string | null
          status?: string
          stripe_payment_intent_id?: string | null
        }
        Update: {
          agent_id?: string | null
          amount_usd?: number | null
          approved_at?: string | null
          approved_by?: string | null
          client_id?: string
          created_at?: string
          id?: string
          requested_by?: string | null
          status?: string
          stripe_payment_intent_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "upsell_requests_agent_id_fkey"
            columns: ["agent_id"]
            isOneToOne: false
            referencedRelation: "agents"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "upsell_requests_client_id_fkey"
            columns: ["client_id"]
            isOneToOne: false
            referencedRelation: "clients"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      agent_performance_stats: {
        Row: {
          accuracy_rate: number | null
          agent_code: string | null
          avg_confidence: number | null
          avg_confidence_when_correct: number | null
          avg_confidence_when_wrong: number | null
          correct_count: number | null
          incorrect_count: number | null
          pending_evaluation: number | null
          total_decisions: number | null
        }
        Relationships: []
      }
    }
    Functions: {
      find_similar_memories: {
        Args: {
          limit_count?: number
          min_similarity?: number
          query_embedding: string
          target_agent_code: string
          target_client_id?: string
        }
        Returns: {
          confidence: number
          context: string
          decision: string
          id: string
          reasoning: string
          similarity: number
          was_correct: boolean
        }[]
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {},
  },
} as const
