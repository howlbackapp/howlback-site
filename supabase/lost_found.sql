-- Howlback lost & found: tables, privacy rules, and photo storage.
-- Run once in the Supabase SQL editor.

create table if not exists public.lost_found (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  kind text not null check (kind in ('lost','found')),
  city text not null check (char_length(city) <= 60),
  area text check (char_length(area) <= 120),
  seen_on date,
  dog_name text check (char_length(dog_name) <= 60),
  description text not null check (char_length(description) between 10 and 1000),
  photo_path text not null check (char_length(photo_path) <= 200),
  contact_name text check (char_length(contact_name) <= 80),
  contact_phone text check (char_length(contact_phone) <= 30),
  contact_email text check (char_length(contact_email) <= 120),
  show_phone boolean not null default false,
  status text not null default 'pending' check (status in ('pending','approved','rejected','reunited')),
  reviewed_at timestamptz,
  constraint has_contact check (contact_phone is not null or contact_email is not null)
);

create table if not exists public.lost_found_messages (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  post_id uuid not null references public.lost_found(id) on delete cascade,
  from_name text check (char_length(from_name) <= 80),
  from_contact text not null check (char_length(from_contact) <= 120),
  message text not null check (char_length(message) between 5 and 1000),
  handled boolean not null default false
);

alter table public.lost_found enable row level security;
alter table public.lost_found_messages enable row level security;

-- Anyone can submit a post, but it always starts as pending.
drop policy if exists "submit post" on public.lost_found;
create policy "submit post" on public.lost_found for insert to anon, authenticated
  with check (status = 'pending' and reviewed_at is null);

-- Only the Howlback admin can see full posts (with contact info) and approve them.
drop policy if exists "admin posts" on public.lost_found;
create policy "admin posts" on public.lost_found for all to authenticated
  using ((auth.jwt() ->> 'email') = 'hello@howlback.app')
  with check ((auth.jwt() ->> 'email') = 'hello@howlback.app');

-- Anyone can message a poster; only the admin can read messages.
drop policy if exists "send message" on public.lost_found_messages;
create policy "send message" on public.lost_found_messages for insert to anon, authenticated
  with check (handled = false);
drop policy if exists "admin messages" on public.lost_found_messages;
create policy "admin messages" on public.lost_found_messages for all to authenticated
  using ((auth.jwt() ->> 'email') = 'hello@howlback.app')
  with check ((auth.jwt() ->> 'email') = 'hello@howlback.app');

-- Public board: approved posts only, no email, phone only if the poster chose to show it.
create or replace view public.lost_found_public as
  select id, created_at, kind, city, area, seen_on, dog_name, description, photo_path,
         case when show_phone then contact_phone end as phone,
         status, reviewed_at
  from public.lost_found
  where status in ('approved','reunited');

revoke all on public.lost_found from anon;
grant insert on public.lost_found to anon;
revoke all on public.lost_found_messages from anon;
grant insert on public.lost_found_messages to anon;
grant select on public.lost_found_public to anon, authenticated;

-- Photo storage: images only, 8 MB max, upload-only for the public.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('lost-found', 'lost-found', true, 8388608,
        array['image/jpeg','image/png','image/webp','image/heic','image/heif'])
on conflict (id) do nothing;

drop policy if exists "upload lost-found photo" on storage.objects;
create policy "upload lost-found photo" on storage.objects for insert to anon, authenticated
  with check (bucket_id = 'lost-found');
