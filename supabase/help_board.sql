-- Howlback help board: people ask for a ride or supplies for a dog, neighbors offer to help.
-- Run once in the Supabase SQL editor. Safe to re-run.
create extension if not exists pg_net;

create table if not exists public.help_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  kind text not null check (kind in ('ride','supplies','other')),
  city text not null check (char_length(city) <= 60),
  title text not null check (char_length(title) between 5 and 100),
  details text not null check (char_length(details) between 10 and 1000),
  needed_by date,
  contact_name text check (char_length(contact_name) <= 80),
  contact_phone text check (char_length(contact_phone) <= 30),
  contact_email text check (char_length(contact_email) <= 120),
  show_phone boolean not null default false,
  edit_token uuid,
  status text not null default 'pending' check (status in ('pending','approved','rejected','done')),
  reviewed_at timestamptz,
  done_at timestamptz,
  constraint help_has_contact check (contact_phone is not null or contact_email is not null)
);

create table if not exists public.help_offers (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  request_id uuid not null references public.help_requests(id) on delete cascade,
  from_name text check (char_length(from_name) <= 80),
  from_contact text not null check (char_length(from_contact) <= 120),
  message text not null check (char_length(message) between 5 and 1000),
  handled boolean not null default false
);

alter table public.help_requests enable row level security;
alter table public.help_offers enable row level security;

-- Anyone can ask for help, but it always starts as pending.
drop policy if exists "submit help" on public.help_requests;
create policy "submit help" on public.help_requests for insert to anon, authenticated
  with check (status = 'pending' and reviewed_at is null and done_at is null);
drop policy if exists "admin help" on public.help_requests;
create policy "admin help" on public.help_requests for all to authenticated
  using ((auth.jwt() ->> 'email') = 'hello@howlback.app')
  with check ((auth.jwt() ->> 'email') = 'hello@howlback.app');

-- Anyone can offer to help; only the admin reads offers and passes them on.
drop policy if exists "send offer" on public.help_offers;
create policy "send offer" on public.help_offers for insert to anon, authenticated
  with check (handled = false);
drop policy if exists "admin offers" on public.help_offers;
create policy "admin offers" on public.help_offers for all to authenticated
  using ((auth.jwt() ->> 'email') = 'hello@howlback.app')
  with check ((auth.jwt() ->> 'email') = 'hello@howlback.app');

revoke all on public.help_requests, public.help_offers from anon;
grant insert on public.help_requests, public.help_offers to anon;
grant select, insert, update, delete on public.help_requests, public.help_offers to authenticated;

-- Public board: approved requests for 30 days (or until the needed-by date passes), done ones for 2 days. No email.
create or replace view public.help_public as
  select id, created_at, kind, city, title, details, needed_by,
         case when show_phone then contact_phone end as phone, status
  from public.help_requests
  where (status = 'approved' and created_at > now() - interval '30 days'
         and (needed_by is null or needed_by >= current_date - 1))
     or (status = 'done' and done_at > now() - interval '2 days');
grant select on public.help_public to anon, authenticated;

-- Poster marks their own request done with the private link they got after posting.
create or replace function public.help_mark_done(p_id uuid, p_token uuid) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  update public.help_requests set status = 'done', done_at = now()
   where id = p_id and edit_token = p_token and p_token is not null and status in ('approved','pending');
  return found;
end $$;
revoke all on function public.help_mark_done(uuid, uuid) from public;
grant execute on function public.help_mark_done(uuid, uuid) to anon, authenticated;

-- Phone alert when something is waiting.
create or replace function public.help_notify() returns trigger
language plpgsql security definer set search_path = public, extensions as $$
declare t text; m text;
begin
  if tg_table_name = 'help_requests' then
    t := 'New help board request';
    m := new.title || ' · ' || new.city || '. Tap to review.';
  else
    t := 'Someone offered to help';
    m := 'A neighbor answered a help board request. Tap to pass it on.';
  end if;
  perform net.http_post(url := 'https://ntfy.sh/',
    body := jsonb_build_object('topic', 'howlback-lf-3ef6dc8085473615', 'title', t, 'message', m,
      'click', 'https://howlback.app/admin/', 'tags', jsonb_build_array('dog')),
    headers := '{"Content-Type": "application/json"}'::jsonb);
  return new;
end $$;
drop trigger if exists help_notify_req on public.help_requests;
create trigger help_notify_req after insert on public.help_requests for each row execute function public.help_notify();
drop trigger if exists help_notify_offer on public.help_offers;
create trigger help_notify_offer after insert on public.help_offers for each row execute function public.help_notify();
