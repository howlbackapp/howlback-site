-- Reunited button for posters, and automatic expiry.
-- Lost posts show 60 days, found posts 30 days. Reunited posts show 24 hours, then drop off.
alter table public.lost_found add column if not exists edit_token uuid;
alter table public.lost_found add column if not exists reunited_at timestamptz;

-- Poster marks their own post reunited with the private link they got after posting.
create or replace function public.lf_mark_reunited(p_id uuid, p_token uuid) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  update public.lost_found set status = 'reunited', reunited_at = now()
   where id = p_id and edit_token = p_token and p_token is not null and status in ('approved','pending');
  return found;
end $$;
revoke all on function public.lf_mark_reunited(uuid, uuid) from public;
grant execute on function public.lf_mark_reunited(uuid, uuid) to anon, authenticated;

create or replace view public.lost_found_public as
  select id, created_at, kind, city, area, seen_on, dog_name, description, photo_path,
         case when show_phone then contact_phone end as phone,
         status, reviewed_at, reunited_at
  from public.lost_found
  where (status = 'approved' and created_at > now() - case when kind = 'lost' then interval '60 days' else interval '30 days' end)
     or (status = 'reunited' and reunited_at > now() - interval '24 hours');
grant select on public.lost_found_public to anon, authenticated;
