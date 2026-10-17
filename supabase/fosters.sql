-- Howlback fosters: foster profiles, dogs, verified receipts, and supporter payments.
-- Run once in the Supabase SQL editor. Safe to re-run.

create or replace function public.is_admin() returns boolean
language sql stable as $$ select coalesce(auth.jwt() ->> 'email', '') = 'hello@howlback.app' $$;

-- ---------- tables ----------
create table if not exists public.fosters (
  id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  name text not null check (char_length(name) between 2 and 80),
  city text not null check (char_length(city) <= 60),
  phone text check (char_length(phone) <= 30),
  about text check (char_length(about) <= 1000),
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  stripe_account_id text,
  payouts_ready boolean not null default false,
  reviewed_at timestamptz
);

create table if not exists public.dogs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foster_id uuid not null references public.fosters(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 60),
  sex text check (sex in ('male','female','unknown')),
  age text check (char_length(age) <= 30),
  breed text check (char_length(breed) <= 60),
  city text not null check (char_length(city) <= 60),
  story text not null check (char_length(story) between 20 and 2000),
  photo_path text not null check (char_length(photo_path) <= 200),
  status text not null default 'pending' check (status in ('pending','live','adopted','rejected','hidden')),
  reviewed_at timestamptz
);

create table if not exists public.expenses (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  dog_id uuid not null references public.dogs(id) on delete cascade,
  foster_id uuid not null references public.fosters(id) on delete cascade,
  category text not null check (category in ('vet','meds','food','supplies','toys','grooming','other')),
  business_name text not null check (char_length(business_name) between 2 and 100),
  note text check (char_length(note) <= 300),
  amount_cents integer not null check (amount_cents between 100 and 500000),
  spent_on date not null,
  receipt_path text not null check (char_length(receipt_path) <= 200),
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  review_note text check (char_length(review_note) <= 300),
  funded_cents integer not null default 0 check (funded_cents >= 0),
  paid_out_cents integer not null default 0 check (paid_out_cents >= 0),
  reviewed_at timestamptz
);

create table if not exists public.contributions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  expense_id uuid not null references public.expenses(id) on delete restrict,
  amount_cents integer not null check (amount_cents >= 100),
  fee_cents integer not null check (fee_cents >= 0),
  total_cents integer not null,
  fee_percent numeric(5,2) not null,
  supporter_name text check (char_length(supporter_name) <= 60),
  supporter_note text check (char_length(supporter_note) <= 200),
  stripe_session_id text unique,
  stripe_payment_intent text,
  status text not null default 'pending' check (status in ('pending','paid','refunded','failed'))
);

-- ---------- guard rails: only the admin can approve or change money fields ----------
create or replace function public.guard_foster() returns trigger language plpgsql as $$
begin
  if public.is_admin() or auth.role() = 'service_role' then return new; end if;
  if tg_op = 'INSERT' then
    new.status := 'pending'; new.stripe_account_id := null; new.payouts_ready := false; new.reviewed_at := null;
  else
    new.status := old.status; new.stripe_account_id := old.stripe_account_id;
    new.payouts_ready := old.payouts_ready; new.reviewed_at := old.reviewed_at; new.id := old.id;
  end if;
  return new;
end $$;
drop trigger if exists guard_foster on public.fosters;
create trigger guard_foster before insert or update on public.fosters for each row execute function public.guard_foster();

create or replace function public.guard_dog() returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  if public.is_admin() or auth.role() = 'service_role' then return new; end if;
  if tg_op = 'INSERT' then
    new.status := 'pending'; new.reviewed_at := null;
  else
    new.foster_id := old.foster_id; new.reviewed_at := old.reviewed_at;
    -- a foster can mark a live dog adopted or hide it, nothing else
    if not (old.status = 'live' and new.status in ('adopted','hidden')) and not (old.status = 'hidden' and new.status = 'live') then
      new.status := old.status;
    end if;
  end if;
  return new;
end $$;
drop trigger if exists guard_dog on public.dogs;
create trigger guard_dog before insert or update on public.dogs for each row execute function public.guard_dog();

create or replace function public.guard_expense() returns trigger language plpgsql as $$
begin
  if public.is_admin() or auth.role() = 'service_role' then return new; end if;
  if tg_op = 'INSERT' then
    new.status := 'pending'; new.review_note := null; new.reviewed_at := null;
    new.funded_cents := 0; new.paid_out_cents := 0;
    if not exists (select 1 from public.dogs d where d.id = new.dog_id and d.foster_id = auth.uid()) then
      raise exception 'not your dog';
    end if;
  else
    -- once a receipt is reviewed, the foster can't change it
    if old.status <> 'pending' then raise exception 'receipt already reviewed'; end if;
    new.status := old.status; new.funded_cents := old.funded_cents; new.paid_out_cents := old.paid_out_cents;
    new.foster_id := old.foster_id; new.dog_id := old.dog_id;
  end if;
  return new;
end $$;
drop trigger if exists guard_expense on public.expenses;
create trigger guard_expense before insert or update on public.expenses for each row execute function public.guard_expense();

-- ---------- row level security ----------
alter table public.fosters enable row level security;
alter table public.dogs enable row level security;
alter table public.expenses enable row level security;
alter table public.contributions enable row level security;

drop policy if exists "own foster" on public.fosters;
create policy "own foster" on public.fosters for all to authenticated
  using (id = auth.uid() or public.is_admin()) with check (id = auth.uid() or public.is_admin());

drop policy if exists "own dogs" on public.dogs;
create policy "own dogs" on public.dogs for all to authenticated
  using (foster_id = auth.uid() or public.is_admin()) with check (foster_id = auth.uid() or public.is_admin());

drop policy if exists "own expenses" on public.expenses;
create policy "own expenses" on public.expenses for all to authenticated
  using (foster_id = auth.uid() or public.is_admin()) with check (foster_id = auth.uid() or public.is_admin());

drop policy if exists "admin contributions" on public.contributions;
create policy "admin contributions" on public.contributions for select to authenticated
  using (public.is_admin() or exists (select 1 from public.expenses e where e.id = expense_id and e.foster_id = auth.uid()));

revoke all on public.fosters, public.dogs, public.expenses, public.contributions from anon;

-- ---------- public views (no phone, no receipts, no Stripe ids) ----------
create or replace view public.dogs_public as
  select d.id, d.created_at, d.name, d.sex, d.age, d.breed, d.city, d.story, d.photo_path, d.status,
         split_part(f.name, ' ', 1) as foster_first_name,
         coalesce((select sum(e.amount_cents) from public.expenses e where e.dog_id = d.id and e.status = 'approved'), 0) as needed_cents,
         coalesce((select sum(e.funded_cents) from public.expenses e where e.dog_id = d.id and e.status = 'approved'), 0) as funded_cents
  from public.dogs d join public.fosters f on f.id = d.foster_id
  where d.status in ('live','adopted') and f.status = 'approved';

create or replace view public.expenses_public as
  select e.id, e.created_at, e.dog_id, e.category, e.business_name, e.note, e.amount_cents, e.spent_on, e.funded_cents
  from public.expenses e join public.dogs_public d on d.id = e.dog_id
  where e.status = 'approved';

create or replace view public.contributions_public as
  select c.expense_id, e.dog_id, c.created_at, c.amount_cents,
         coalesce(nullif(c.supporter_name, ''), 'Someone') as supporter_name, c.supporter_note
  from public.contributions c join public.expenses e on e.id = c.expense_id
  where c.status = 'paid';

grant select on public.dogs_public, public.expenses_public, public.contributions_public to anon, authenticated;

-- ---------- storage ----------
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('dogs', 'dogs', true, 8388608, array['image/jpeg','image/png','image/webp'])
on conflict (id) do nothing;
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('receipts', 'receipts', false, 10485760, array['image/jpeg','image/png','image/webp','application/pdf'])
on conflict (id) do nothing;

-- files go in a folder named after the foster's user id
drop policy if exists "foster dog photos" on storage.objects;
create policy "foster dog photos" on storage.objects for insert to authenticated
  with check (bucket_id = 'dogs' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "foster receipts upload" on storage.objects;
create policy "foster receipts upload" on storage.objects for insert to authenticated
  with check (bucket_id = 'receipts' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "foster receipts read" on storage.objects;
create policy "foster receipts read" on storage.objects for select to authenticated
  using (bucket_id = 'receipts' and ((storage.foldername(name))[1] = auth.uid()::text or public.is_admin()));

-- ---------- phone alerts for things waiting on review ----------
create or replace function public.foster_notify() returns trigger language plpgsql security definer as $$
declare t text; m text;
begin
  if tg_table_name = 'fosters' then t := 'New foster sign-up'; m := new.name || ' · ' || new.city;
  elsif tg_table_name = 'dogs' then t := 'New dog profile waiting'; m := new.name || ' · ' || new.city;
  elsif tg_table_name = 'expenses' then t := 'New receipt to verify'; m := new.business_name || ' · $' || to_char(new.amount_cents / 100.0, 'FM999990.00');
  else t := 'New payment 💸'; m := '$' || to_char(new.amount_cents / 100.0, 'FM999990.00') || ' toward a receipt (+ $' || to_char(new.fee_cents / 100.0, 'FM999990.00') || ' fee)';
  end if;
  perform net.http_post(url := 'https://ntfy.sh/',
    body := jsonb_build_object('topic', 'howlback-lf-3ef6dc8085473615', 'title', t, 'message', m,
      'click', 'https://howlback.app/admin/', 'tags', jsonb_build_array('dog')),
    headers := '{"Content-Type": "application/json"}'::jsonb);
  return new;
end $$;
drop trigger if exists foster_notify on public.fosters;
create trigger foster_notify after insert on public.fosters for each row execute function public.foster_notify();
drop trigger if exists dog_notify on public.dogs;
create trigger dog_notify after insert on public.dogs for each row execute function public.foster_notify();
drop trigger if exists expense_notify on public.expenses;
create trigger expense_notify after insert on public.expenses for each row execute function public.foster_notify();
drop trigger if exists contribution_notify on public.contributions;
create trigger contribution_notify after update of status on public.contributions for each row
  when (new.status = 'paid' and old.status <> 'paid') execute function public.foster_notify();
